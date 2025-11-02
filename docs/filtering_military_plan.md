Regola robusta (da applicare a tutti i record):

Escludi tutte le righe con awarding_agency_code = '097' OR funding_agency_code = '097' (097 = Department of Defense). 
usaspending.gov
+1

Escludi anche dove awarding_agency_name o funding_agency_name contengono parole chiave tipo "DEFENSE", "DEPARTMENT OF THE ARMY", "DEPARTMENT OF THE NAVY", "DEPARTMENT OF THE AIR FORCE" (alcuni sub-agency possono apparire per nome). 
whitehouse.gov

Se la tabella ha campi DoD-specifici (dod_claimant_program_code, dod_claimant_program_description, dod_acquisition_program_code, dod_acquisition_program_description), escludi qualsiasi record con questi campi non nulli — sono un segnale diretto di legami militari.

Subawards (prima-tier subawards):

Usa gli stessi filtri sulle colonne prime_award_awarding_agency_code / prime_award_awarding_agency_name e prime_award_funding_agency_code / prime_award_funding_agency_name per rimuovere subaward collegati a prime DoD. 
files.usaspending.gov

Suggerimento pratico — file di lookup:

Scarica agency_codes.csv da USAspending (reference_data) e usa quella mappatura per filtrare tutti i codici che mappano al Dipartimento della Difesa o ai suoi bureau/sub-agencies (non solo 097; verificare eventuali codici correlati o spostamenti storici). 
files.usaspending.gov