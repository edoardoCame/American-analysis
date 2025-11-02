"""Utility functions per analisi di mercato sulle opportunità archiviate SAM.

Il modulo gestisce il caricamento del database SQLite, la normalizzazione dei
campi principali e la produzione di aggregazioni pronte per grafici e tabelle.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class DatasetInfo:
    """Metadati di supporto per comprendere il contenuto del database."""

    table: str
    fiscal_year: int
    rows: int


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """Restituisce una connessione SQLite in sola lettura."""

    # `uri=True` permette di usare la flag `mode=ro` evitando scritture involontarie.
    path = Path(db_path).resolve()
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    # Alcuni record contengono stringhe fuori UTF-8: forziamo la decodifica sostituendo i caratteri invalidi.
    conn.text_factory = lambda b: (
        b.decode("utf-8", "replace") if isinstance(b, (bytes, bytearray)) else str(b)
    )
    return conn


def list_archived_tables(conn: sqlite3.Connection) -> list[DatasetInfo]:
    """Elenca le tabelle rilevanti che seguono il naming SAM."""

    # Non possiamo parametrizzare il nome della tabella nella subquery,
    # quindi ricaviamo le cardinalità iterando lato Python.
    tables = (
        pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?",
            conn,
            params=("fy%_archived_opportunities",),
        )
        .sort_values("name")
        .reset_index(drop=True)
    )

    output: list[DatasetInfo] = []
    for table in tables["name"]:
        fiscal_year = int(table[2:6])  # fyYYYY
        rows = pd.read_sql(f"SELECT COUNT(1) AS c FROM '{table}'", conn)["c"].iat[0]
        output.append(DatasetInfo(table=table, fiscal_year=fiscal_year, rows=rows))
    return output


def load_opportunities(db_path: str | Path, include_empty: bool = False) -> pd.DataFrame:
    """Carica tutte le tabelle unite in un unico DataFrame con colonna `FiscalYear`."""

    with get_connection(db_path) as conn:
        tables = list_archived_tables(conn)
        frames: list[pd.DataFrame] = []
        for info in tables:
            if not include_empty and info.rows == 0:
                continue
            frame = pd.read_sql(f"SELECT * FROM '{info.table}'", conn)
            frame["FiscalYear"] = info.fiscal_year
            frames.append(frame)
    if not frames:
        raise ValueError("Nessuna tabella con righe trovata nel database")
    df = pd.concat(frames, ignore_index=True)
    return df


def _parse_currency(series: pd.Series) -> pd.Series:
    """Converte valori monetari SAM in float, gestendo simboli e spazi."""

    cleaned = (
        series.astype(str)
        .str.replace(r"[^0-9.]+", "", regex=True)
        .replace("", pd.NA)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def enrich_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizza le colonne principali e calcola metriche derivate."""

    result = df.copy()
    date_columns = {
        "PostedDate": "PostedDate",
        "ArchiveDate": "ArchiveDate",
        "ResponseDeadLine": "ResponseDeadline",
        "AwardDate": "AwardDate",
    }
    for source, target in date_columns.items():
        if source in result:
            parsed = pd.to_datetime(result[source], errors="coerce", utc=True)
            result[target] = parsed.dt.tz_convert(None)

    if "Award$" in result:
        result["AwardAmount"] = _parse_currency(result["Award$"])

    if {"ResponseDeadline", "PostedDate"}.issubset(result.columns):
        response_deadline = pd.to_datetime(result["ResponseDeadline"], errors="coerce")
        posted_date = pd.to_datetime(result["PostedDate"], errors="coerce")
        result["ResponseWindowDays"] = (response_deadline - posted_date).dt.days

    textual = [
        "Department/Ind.Agency",
        "Sub-Tier",
        "Type",
        "BaseType",
        "SetASide",
        "SetASideCode",
        "ClassificationCode",
        "NaicsCode",
        "PopState",
        "PopCountry",
        "State",
        "City",
        "Awardee",
    ]
    for column in textual:
        if column in result:
            result[column] = result[column].fillna("Unknown").str.strip()

    return result


def subset_fields(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Restituisce un sottoinsieme di colonne presenti nel DataFrame."""

    existing = [c for c in columns if c in df.columns]
    return df[existing].copy()


def yearly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Crea sintesi annuale di volumi, valori e tempi di risposta."""

    summary = (
        df.groupby("FiscalYear")
        .agg(
            total_opportunities=("NoticeId", "count"),
            total_awarded=("AwardAmount", "sum"),
            median_award=("AwardAmount", "median"),
            avg_award=("AwardAmount", "mean"),
            median_response_window_days=("ResponseWindowDays", "median"),
        )
        .reset_index()
    )
    return summary.fillna(0)


def agency_mix(df: pd.DataFrame, column: str = "Department/Ind.Agency", top_n: int = 15) -> pd.DataFrame:
    """Ranking di agenzie o sub-tier per numero e valore di opportunità."""

    if column not in df:
        raise KeyError(f"Colonna {column} non presente nel dataset")

    aggregated = (
        df.groupby(column)
        .agg(
            opportunities=("NoticeId", "count"),
            total_award=("AwardAmount", "sum"),
            median_award=("AwardAmount", "median"),
        )
        .sort_values(["opportunities", "total_award"], ascending=False)
        .head(top_n)
        .reset_index()
        .rename(columns={column: "entity"})
    )
    return aggregated


def naics_opportunity_matrix(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Restituisce i settori NAICS più attivi con valore e frequenza."""

    if "NaicsCode" not in df:
        raise KeyError("Colonna NaicsCode non presente nel dataset")

    naics = (
        df.groupby(["FiscalYear", "NaicsCode"])
        .agg(
            opportunities=("NoticeId", "count"),
            total_award=("AwardAmount", "sum"),
        )
        .reset_index()
    )
    totals = (
        naics.groupby("NaicsCode")["opportunities"].sum().sort_values(ascending=False)
    )
    top_codes = totals.head(top_n).index
    filtered = naics[naics["NaicsCode"].isin(top_codes)]
    return filtered


def set_aside_landscape(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Analizza la distribuzione dei programmi di Set Aside."""

    if "SetASide" not in df:
        raise KeyError("Colonna SetASide non presente nel dataset")

    mix = (
        df.groupby("SetASide")
        .agg(
            opportunities=("NoticeId", "count"),
            total_award=("AwardAmount", "sum"),
        )
        .sort_values("opportunities", ascending=False)
        .head(top_n)
        .reset_index()
    )
    total_ops = mix["opportunities"].sum()
    if total_ops:
        mix["share"] = mix["opportunities"] / total_ops
    else:
        mix["share"] = 0
    return mix


def geographic_distribution(df: pd.DataFrame, level: str = "State") -> pd.DataFrame:
    """Aggrega le opportunità per area geografica (stato o paese)."""

    if level not in df:
        raise KeyError(f"Colonna {level} non presente nel dataset")

    geo = (
        df.groupby(level)
        .agg(
            opportunities=("NoticeId", "count"),
            total_award=("AwardAmount", "sum"),
        )
        .reset_index()
        .sort_values("opportunities", ascending=False)
    )
    return geo


def timeline_by_quarter(df: pd.DataFrame) -> pd.DataFrame:
    """Costruisce una serie temporale trimestrale di opportunità e valori."""

    if "PostedDate" not in df:
        raise KeyError("PostedDate mancante per la timeline")

    timeline = (
        df.dropna(subset=["PostedDate"])
        .assign(Quarter=lambda d: d["PostedDate"].dt.to_period("Q"))
        .groupby("Quarter")
        .agg(
            opportunities=("NoticeId", "count"),
            total_award=("AwardAmount", "sum"),
            median_response_days=("ResponseWindowDays", "median"),
        )
        .reset_index()
    )
    timeline["Quarter"] = timeline["Quarter"].dt.to_timestamp()
    return timeline


def opportunity_duration_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Restituisce la distribuzione dei tempi di risposta."""

    if "ResponseWindowDays" not in df:
        raise KeyError("ResponseWindowDays non calcolato")

    return df[["FiscalYear", "ResponseWindowDays"]].dropna()


def awardee_leaderboard(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Individua gli assegnatari con maggior valore e frequenza di aggiudicazioni."""

    if "Awardee" not in df:
        raise KeyError("Colonna Awardee non presente nel dataset")

    leaderboard = (
        df[df["AwardAmount"].notna()]
        .groupby("Awardee")
        .agg(
            total_award=("AwardAmount", "sum"),
            avg_award=("AwardAmount", "mean"),
            median_award=("AwardAmount", "median"),
            awards_count=("AwardAmount", "count"),
            opportunities=("NoticeId", "nunique"),
        )
        .sort_values("total_award", ascending=False)
        .head(top_n)
        .reset_index()
    )
    return leaderboard


def award_concentration(df: pd.DataFrame, top_k: int = 50) -> pd.DataFrame:
    """Calcola la curva di concentrazione del valore aggiudicato sui principali awardee."""

    board = awardee_leaderboard(df, top_n=top_k)
    total = df["AwardAmount"].sum()
    if total == 0:
        board["share"] = 0
        board["cumulative_share"] = 0
        return board

    board["share"] = board["total_award"] / total
    board["cumulative_share"] = board["share"].cumsum()
    return board


def award_amount_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Restituisce statistiche descrittive sui valori di aggiudicazione."""

    if "AwardAmount" not in df:
        raise KeyError("AwardAmount non calcolato: eseguire enrich_dataset")

    summary = df["AwardAmount"].dropna()
    return summary.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]).to_frame(name="AwardAmount")


__all__ = [
    "DatasetInfo",
    "agency_mix",
    "enrich_dataset",
    "geographic_distribution",
    "get_connection",
    "list_archived_tables",
    "load_opportunities",
    "naics_opportunity_matrix",
    "opportunity_duration_profile",
    "set_aside_landscape",
    "subset_fields",
    "timeline_by_quarter",
    "awardee_leaderboard",
    "award_concentration",
    "award_amount_summary",
    "yearly_summary",
]
