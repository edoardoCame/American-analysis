# Prime Transactions e Subawards — Estratto 2025-10-22

## Riepilogo file
- `Assistance_PrimeTransactions_2025-10-22_H14M19S41_1.csv`: 0 righe, 112 colonne
- `Assistance_Subawards_2025-10-22_H14M19S47_1.csv`: 0 righe, 113 colonne
- `Contracts_PrimeTransactions_2025-10-22_H14M09S33_1.csv`: 238078 righe, 297 colonne
- `Contracts_Subawards_2025-10-22_H14M19S43_1.csv`: 516 righe, 118 colonne

## Database e filtri NAICS
- `db/prime_transactions.sqlite` contiene le 4 tabelle dell'estratto (2 Contracts, 2 Assistance).
- `db/prime_transactions_filtered.sqlite` ora contiene solo i record con `naics_code = 561612` (Security Guards and Patrol Services):
  - `contracts_primetransactions_2025_10_22_h14m09s33_1`: 238078 righe
  - `contracts_subawards_2025_10_22_h14m19s43_1`: 253 righe
  - Nessuna tabella Assistance in questo DB filtrato.

## Dettagli per file
### Assistance_PrimeTransactions_2025-10-22_H14M19S41_1.csv
- Righe: 0
- Numero colonne: 112
- Elenco colonne:
  - assistance_transaction_unique_key
  - assistance_award_unique_key
  - award_id_fain
  - modification_number
  - award_id_uri
  - sai_number
  - federal_action_obligation
  - total_obligated_amount
  - total_outlayed_amount_for_overall_award
  - indirect_cost_federal_share_amount
  - non_federal_funding_amount
  - total_non_federal_funding_amount
  - face_value_of_loan
  - original_loan_subsidy_cost
  - total_face_value_of_loan
  - total_loan_subsidy_cost
  - generated_pragmatic_obligations
  - disaster_emergency_fund_codes_for_overall_award
  - outlayed_amount_from_COVID-19_supplementals_for_overall_award
  - obligated_amount_from_COVID-19_supplementals_for_overall_award
  - outlayed_amount_from_IIJA_supplemental_for_overall_award
  - obligated_amount_from_IIJA_supplemental_for_overall_award
  - action_date
  - action_date_fiscal_year
  - period_of_performance_start_date
  - period_of_performance_current_end_date
  - awarding_agency_code
  - awarding_agency_name
  - awarding_sub_agency_code
  - awarding_sub_agency_name
  - awarding_office_code
  - awarding_office_name
  - funding_agency_code
  - funding_agency_name
  - funding_sub_agency_code
  - funding_sub_agency_name
  - funding_office_code
  - funding_office_name
  - treasury_accounts_funding_this_award
  - federal_accounts_funding_this_award
  - object_classes_funding_this_award
  - program_activities_funding_this_award
  - recipient_uei
  - recipient_duns
  - recipient_name
  - recipient_name_raw
  - recipient_parent_uei
  - recipient_parent_duns
  - recipient_parent_name
  - recipient_parent_name_raw
  - recipient_country_code
  - recipient_country_name
  - recipient_address_line_1
  - recipient_address_line_2
  - recipient_city_code
  - recipient_city_name
  - prime_award_transaction_recipient_county_fips_code
  - recipient_county_name
  - prime_award_transaction_recipient_state_fips_code
  - recipient_state_code
  - recipient_state_name
  - recipient_zip_code
  - recipient_zip_last_4_code
  - prime_award_transaction_recipient_cd_original
  - prime_award_transaction_recipient_cd_current
  - recipient_foreign_city_name
  - recipient_foreign_province_name
  - recipient_foreign_postal_code
  - primary_place_of_performance_scope
  - primary_place_of_performance_country_code
  - primary_place_of_performance_country_name
  - primary_place_of_performance_code
  - primary_place_of_performance_city_name
  - prime_award_transaction_place_of_performance_county_fips_code
  - primary_place_of_performance_county_name
  - prime_award_transaction_place_of_performance_state_fips_code
  - primary_place_of_performance_state_name
  - primary_place_of_performance_zip_4
  - prime_award_transaction_place_of_performance_cd_original
  - prime_award_transaction_place_of_performance_cd_current
  - primary_place_of_performance_foreign_location
  - cfda_number
  - cfda_title
  - funding_opportunity_number
  - funding_opportunity_goals_text
  - assistance_type_code
  - assistance_type_description
  - transaction_description
  - prime_award_base_transaction_description
  - business_funds_indicator_code
  - business_funds_indicator_description
  - business_types_code
  - business_types_description
  - correction_delete_indicator_code
  - correction_delete_indicator_description
  - action_type_code
  - action_type_description
  - record_type_code
  - record_type_description
  - highly_compensated_officer_1_name
  - highly_compensated_officer_1_amount
  - highly_compensated_officer_2_name
  - highly_compensated_officer_2_amount
  - highly_compensated_officer_3_name
  - highly_compensated_officer_3_amount
  - highly_compensated_officer_4_name
  - highly_compensated_officer_4_amount
  - highly_compensated_officer_5_name
  - highly_compensated_officer_5_amount
  - usaspending_permalink
  - initial_report_date
  - last_modified_date

### Assistance_Subawards_2025-10-22_H14M19S47_1.csv
- Righe: 0
- Numero colonne: 113
- Elenco colonne:
  - prime_award_unique_key
  - prime_award_fain
  - prime_award_amount
  - prime_award_disaster_emergency_fund_codes
  - prime_award_outlayed_amount_from_COVID-19_supplementals
  - prime_award_obligated_amount_from_COVID-19_supplementals
  - prime_award_outlayed_amount_from_IIJA_supplemental
  - prime_award_obligated_amount_from_IIJA_supplemental
  - prime_award_total_outlayed_amount
  - prime_award_base_action_date
  - prime_award_base_action_date_fiscal_year
  - prime_award_latest_action_date
  - prime_award_latest_action_date_fiscal_year
  - prime_award_period_of_performance_start_date
  - prime_award_period_of_performance_current_end_date
  - prime_award_awarding_agency_code
  - prime_award_awarding_agency_name
  - prime_award_awarding_sub_agency_code
  - prime_award_awarding_sub_agency_name
  - prime_award_awarding_office_code
  - prime_award_awarding_office_name
  - prime_award_funding_agency_code
  - prime_award_funding_agency_name
  - prime_award_funding_sub_agency_code
  - prime_award_funding_sub_agency_name
  - prime_award_funding_office_code
  - prime_award_funding_office_name
  - prime_award_treasury_accounts_funding_this_award
  - prime_award_federal_accounts_funding_this_award
  - prime_award_object_classes_funding_this_award
  - prime_award_program_activities_funding_this_award
  - prime_awardee_uei
  - prime_awardee_duns
  - prime_awardee_name
  - prime_awardee_dba_name
  - prime_awardee_parent_uei
  - prime_awardee_parent_duns
  - prime_awardee_parent_name
  - prime_awardee_country_code
  - prime_awardee_country_name
  - prime_awardee_address_line_1
  - prime_awardee_city_name
  - prime_awardee_county_fips_code
  - prime_awardee_county_name
  - prime_awardee_state_fips_code
  - prime_awardee_state_code
  - prime_awardee_state_name
  - prime_awardee_zip_code
  - prime_award_summary_recipient_cd_original
  - prime_award_summary_recipient_cd_current
  - prime_awardee_foreign_postal_code
  - prime_awardee_business_types
  - prime_award_primary_place_of_performance_scope
  - prime_award_primary_place_of_performance_city_name
  - prime_award_primary_place_of_performance_county_fips_code
  - prime_award_primary_place_of_performance_county_name
  - prime_award_primary_place_of_performance_state_fips_code
  - prime_award_primary_place_of_performance_state_code
  - prime_award_primary_place_of_performance_state_name
  - prime_award_primary_place_of_performance_address_zip_code
  - prime_award_summary_place_of_performance_cd_original
  - prime_award_summary_place_of_performance_cd_current
  - prime_award_primary_place_of_performance_country_code
  - prime_award_primary_place_of_performance_country_name
  - prime_award_base_transaction_description
  - prime_award_cfda_numbers_and_titles
  - subaward_type
  - subaward_sam_report_id
  - subaward_sam_report_year
  - subaward_sam_report_month
  - subaward_number
  - subaward_amount
  - subaward_action_date
  - subaward_action_date_fiscal_year
  - subawardee_uei
  - subawardee_duns
  - subawardee_name
  - subawardee_dba_name
  - subawardee_parent_uei
  - subawardee_parent_duns
  - subawardee_parent_name
  - subawardee_country_code
  - subawardee_country_name
  - subawardee_address_line_1
  - subawardee_city_name
  - subawardee_state_code
  - subawardee_state_name
  - subawardee_zip_code
  - subaward_recipient_cd_original
  - subaward_recipient_cd_current
  - subawardee_foreign_postal_code
  - subawardee_business_types
  - subaward_primary_place_of_performance_city_name
  - subaward_primary_place_of_performance_state_code
  - subaward_primary_place_of_performance_state_name
  - subaward_primary_place_of_performance_address_zip_code
  - subaward_place_of_performance_cd_original
  - subaward_place_of_performance_cd_current
  - subaward_primary_place_of_performance_country_code
  - subaward_primary_place_of_performance_country_name
  - subaward_description
  - subawardee_highly_compensated_officer_1_name
  - subawardee_highly_compensated_officer_1_amount
  - subawardee_highly_compensated_officer_2_name
  - subawardee_highly_compensated_officer_2_amount
  - subawardee_highly_compensated_officer_3_name
  - subawardee_highly_compensated_officer_3_amount
  - subawardee_highly_compensated_officer_4_name
  - subawardee_highly_compensated_officer_4_amount
  - subawardee_highly_compensated_officer_5_name
  - subawardee_highly_compensated_officer_5_amount
  - usaspending_permalink
  - subaward_sam_report_last_modified_date

### Contracts_PrimeTransactions_2025-10-22_H14M09S33_1.csv
- Righe: 238078
- Numero colonne: 297
- Elenco colonne:
  - contract_transaction_unique_key
  - contract_award_unique_key
  - award_id_piid
  - modification_number
  - transaction_number
  - parent_award_agency_id
  - parent_award_agency_name
  - parent_award_id_piid
  - parent_award_modification_number
  - federal_action_obligation
  - total_dollars_obligated
  - total_outlayed_amount_for_overall_award
  - base_and_exercised_options_value
  - current_total_value_of_award
  - base_and_all_options_value
  - potential_total_value_of_award
  - disaster_emergency_fund_codes_for_overall_award
  - outlayed_amount_from_COVID-19_supplementals_for_overall_award
  - obligated_amount_from_COVID-19_supplementals_for_overall_award
  - outlayed_amount_from_IIJA_supplemental_for_overall_award
  - obligated_amount_from_IIJA_supplemental_for_overall_award
  - action_date
  - action_date_fiscal_year
  - period_of_performance_start_date
  - period_of_performance_current_end_date
  - period_of_performance_potential_end_date
  - ordering_period_end_date
  - solicitation_date
  - awarding_agency_code
  - awarding_agency_name
  - awarding_sub_agency_code
  - awarding_sub_agency_name
  - awarding_office_code
  - awarding_office_name
  - funding_agency_code
  - funding_agency_name
  - funding_sub_agency_code
  - funding_sub_agency_name
  - funding_office_code
  - funding_office_name
  - treasury_accounts_funding_this_award
  - federal_accounts_funding_this_award
  - object_classes_funding_this_award
  - program_activities_funding_this_award
  - foreign_funding
  - foreign_funding_description
  - sam_exception
  - sam_exception_description
  - recipient_uei
  - recipient_duns
  - recipient_name
  - recipient_name_raw
  - recipient_doing_business_as_name
  - cage_code
  - recipient_parent_uei
  - recipient_parent_duns
  - recipient_parent_name
  - recipient_parent_name_raw
  - recipient_country_code
  - recipient_country_name
  - recipient_address_line_1
  - recipient_address_line_2
  - recipient_city_name
  - prime_award_transaction_recipient_county_fips_code
  - recipient_county_name
  - prime_award_transaction_recipient_state_fips_code
  - recipient_state_code
  - recipient_state_name
  - recipient_zip_4_code
  - prime_award_transaction_recipient_cd_original
  - prime_award_transaction_recipient_cd_current
  - recipient_phone_number
  - recipient_fax_number
  - primary_place_of_performance_country_code
  - primary_place_of_performance_country_name
  - primary_place_of_performance_city_name
  - prime_award_transaction_place_of_performance_county_fips_code
  - primary_place_of_performance_county_name
  - prime_award_transaction_place_of_performance_state_fips_code
  - primary_place_of_performance_state_code
  - primary_place_of_performance_state_name
  - primary_place_of_performance_zip_4
  - prime_award_transaction_place_of_performance_cd_original
  - prime_award_transaction_place_of_performance_cd_current
  - award_or_idv_flag
  - award_type_code
  - award_type
  - idv_type_code
  - idv_type
  - multiple_or_single_award_idv_code
  - multiple_or_single_award_idv
  - type_of_idc_code
  - type_of_idc
  - type_of_contract_pricing_code
  - type_of_contract_pricing
  - transaction_description
  - prime_award_base_transaction_description
  - action_type_code
  - action_type
  - solicitation_identifier
  - number_of_actions
  - inherently_governmental_functions
  - inherently_governmental_functions_description
  - product_or_service_code
  - product_or_service_code_description
  - contract_bundling_code
  - contract_bundling
  - dod_claimant_program_code
  - dod_claimant_program_description
  - naics_code
  - naics_description
  - recovered_materials_sustainability_code
  - recovered_materials_sustainability
  - domestic_or_foreign_entity_code
  - domestic_or_foreign_entity
  - dod_acquisition_program_code
  - dod_acquisition_program_description
  - information_technology_commercial_item_category_code
  - information_technology_commercial_item_category
  - epa_designated_product_code
  - epa_designated_product
  - country_of_product_or_service_origin_code
  - country_of_product_or_service_origin
  - place_of_manufacture_code
  - place_of_manufacture
  - subcontracting_plan_code
  - subcontracting_plan
  - extent_competed_code
  - extent_competed
  - solicitation_procedures_code
  - solicitation_procedures
  - type_of_set_aside_code
  - type_of_set_aside
  - evaluated_preference_code
  - evaluated_preference
  - research_code
  - research
  - fair_opportunity_limited_sources_code
  - fair_opportunity_limited_sources
  - other_than_full_and_open_competition_code
  - other_than_full_and_open_competition
  - number_of_offers_received
  - commercial_item_acquisition_procedures_code
  - commercial_item_acquisition_procedures
  - small_business_competitiveness_demonstration_program
  - simplified_procedures_for_certain_commercial_items_code
  - simplified_procedures_for_certain_commercial_items
  - a76_fair_act_action_code
  - a76_fair_act_action
  - fed_biz_opps_code
  - fed_biz_opps
  - local_area_set_aside_code
  - local_area_set_aside
  - price_evaluation_adjustment_preference_percent_difference
  - clinger_cohen_act_planning_code
  - clinger_cohen_act_planning
  - materials_supplies_articles_equipment_code
  - materials_supplies_articles_equipment
  - labor_standards_code
  - labor_standards
  - construction_wage_rate_requirements_code
  - construction_wage_rate_requirements
  - interagency_contracting_authority_code
  - interagency_contracting_authority
  - other_statutory_authority
  - program_acronym
  - parent_award_type_code
  - parent_award_type
  - parent_award_single_or_multiple_code
  - parent_award_single_or_multiple
  - major_program
  - national_interest_action_code
  - national_interest_action
  - cost_or_pricing_data_code
  - cost_or_pricing_data
  - cost_accounting_standards_clause_code
  - cost_accounting_standards_clause
  - government_furnished_property_code
  - government_furnished_property
  - sea_transportation_code
  - sea_transportation
  - undefinitized_action_code
  - undefinitized_action
  - consolidated_contract_code
  - consolidated_contract
  - performance_based_service_acquisition_code
  - performance_based_service_acquisition
  - multi_year_contract_code
  - multi_year_contract
  - contract_financing_code
  - contract_financing
  - purchase_card_as_payment_method_code
  - purchase_card_as_payment_method
  - contingency_humanitarian_or_peacekeeping_operation_code
  - contingency_humanitarian_or_peacekeeping_operation
  - alaskan_native_corporation_owned_firm
  - american_indian_owned_business
  - indian_tribe_federally_recognized
  - native_hawaiian_organization_owned_firm
  - tribally_owned_firm
  - veteran_owned_business
  - service_disabled_veteran_owned_business
  - woman_owned_business
  - women_owned_small_business
  - economically_disadvantaged_women_owned_small_business
  - joint_venture_women_owned_small_business
  - joint_venture_economic_disadvantaged_women_owned_small_bus
  - minority_owned_business
  - subcontinent_asian_asian_indian_american_owned_business
  - asian_pacific_american_owned_business
  - black_american_owned_business
  - hispanic_american_owned_business
  - native_american_owned_business
  - other_minority_owned_business
  - contracting_officers_determination_of_business_size
  - contracting_officers_determination_of_business_size_code
  - emerging_small_business
  - community_developed_corporation_owned_firm
  - labor_surplus_area_firm
  - us_federal_government
  - federally_funded_research_and_development_corp
  - federal_agency
  - us_state_government
  - us_local_government
  - city_local_government
  - county_local_government
  - inter_municipal_local_government
  - local_government_owned
  - municipality_local_government
  - school_district_local_government
  - township_local_government
  - us_tribal_government
  - foreign_government
  - organizational_type
  - corporate_entity_not_tax_exempt
  - corporate_entity_tax_exempt
  - partnership_or_limited_liability_partnership
  - sole_proprietorship
  - small_agricultural_cooperative
  - international_organization
  - us_government_entity
  - community_development_corporation
  - domestic_shelter
  - educational_institution
  - foundation
  - hospital_flag
  - manufacturer_of_goods
  - veterinary_hospital
  - hispanic_servicing_institution
  - receives_contracts
  - receives_financial_assistance
  - receives_contracts_and_financial_assistance
  - airport_authority
  - council_of_governments
  - housing_authorities_public_tribal
  - interstate_entity
  - planning_commission
  - port_authority
  - transit_authority
  - subchapter_scorporation
  - limited_liability_corporation
  - foreign_owned
  - for_profit_organization
  - nonprofit_organization
  - other_not_for_profit_organization
  - the_ability_one_program
  - private_university_or_college
  - state_controlled_institution_of_higher_learning
  - 1862_land_grant_college
  - 1890_land_grant_college
  - 1994_land_grant_college
  - minority_institution
  - historically_black_college
  - tribal_college
  - alaskan_native_servicing_institution
  - native_hawaiian_servicing_institution
  - school_of_forestry
  - veterinary_college
  - dot_certified_disadvantage
  - self_certified_small_disadvantaged_business
  - small_disadvantaged_business
  - c8a_program_participant
  - historically_underutilized_business_zone_hubzone_firm
  - sba_certified_8a_joint_venture
  - highly_compensated_officer_1_name
  - highly_compensated_officer_1_amount
  - highly_compensated_officer_2_name
  - highly_compensated_officer_2_amount
  - highly_compensated_officer_3_name
  - highly_compensated_officer_3_amount
  - highly_compensated_officer_4_name
  - highly_compensated_officer_4_amount
  - highly_compensated_officer_5_name
  - highly_compensated_officer_5_amount
  - usaspending_permalink
  - initial_report_date
  - last_modified_date

### Contracts_Subawards_2025-10-22_H14M19S43_1.csv
- Righe: 516
- Numero colonne: 118
- Elenco colonne:
  - prime_award_unique_key
  - prime_award_piid
  - prime_award_parent_piid
  - prime_award_amount
  - prime_award_disaster_emergency_fund_codes
  - prime_award_outlayed_amount_from_COVID-19_supplementals
  - prime_award_obligated_amount_from_COVID-19_supplementals
  - prime_award_outlayed_amount_from_IIJA_supplemental
  - prime_award_obligated_amount_from_IIJA_supplemental
  - prime_award_total_outlayed_amount
  - prime_award_base_action_date
  - prime_award_base_action_date_fiscal_year
  - prime_award_latest_action_date
  - prime_award_latest_action_date_fiscal_year
  - prime_award_period_of_performance_start_date
  - prime_award_period_of_performance_current_end_date
  - prime_award_period_of_performance_potential_end_date
  - prime_award_awarding_agency_code
  - prime_award_awarding_agency_name
  - prime_award_awarding_sub_agency_code
  - prime_award_awarding_sub_agency_name
  - prime_award_awarding_office_code
  - prime_award_awarding_office_name
  - prime_award_funding_agency_code
  - prime_award_funding_agency_name
  - prime_award_funding_sub_agency_code
  - prime_award_funding_sub_agency_name
  - prime_award_funding_office_code
  - prime_award_funding_office_name
  - prime_award_treasury_accounts_funding_this_award
  - prime_award_federal_accounts_funding_this_award
  - prime_award_object_classes_funding_this_award
  - prime_award_program_activities_funding_this_award
  - prime_awardee_uei
  - prime_awardee_duns
  - prime_awardee_name
  - prime_awardee_dba_name
  - prime_awardee_parent_uei
  - prime_awardee_parent_duns
  - prime_awardee_parent_name
  - prime_awardee_country_code
  - prime_awardee_country_name
  - prime_awardee_address_line_1
  - prime_awardee_city_name
  - prime_awardee_county_fips_code
  - prime_awardee_county_name
  - prime_awardee_state_fips_code
  - prime_awardee_state_code
  - prime_awardee_state_name
  - prime_awardee_zip_code
  - prime_award_summary_recipient_cd_original
  - prime_award_summary_recipient_cd_current
  - prime_awardee_foreign_postal_code
  - prime_awardee_business_types
  - prime_award_primary_place_of_performance_city_name
  - prime_award_primary_place_of_performance_county_fips_code
  - prime_award_primary_place_of_performance_county_name
  - prime_award_primary_place_of_performance_state_fips_code
  - prime_award_primary_place_of_performance_state_code
  - prime_award_primary_place_of_performance_state_name
  - prime_award_primary_place_of_performance_address_zip_code
  - prime_award_summary_place_of_performance_cd_original
  - prime_award_summary_place_of_performance_cd_current
  - prime_award_primary_place_of_performance_country_code
  - prime_award_primary_place_of_performance_country_name
  - prime_award_base_transaction_description
  - prime_award_project_title
  - prime_award_naics_code
  - prime_award_naics_description
  - prime_award_national_interest_action_code
  - prime_award_national_interest_action
  - subaward_type
  - subaward_sam_report_id
  - subaward_sam_report_year
  - subaward_sam_report_month
  - subaward_number
  - subaward_amount
  - subaward_action_date
  - subaward_action_date_fiscal_year
  - subawardee_uei
  - subawardee_duns
  - subawardee_name
  - subawardee_dba_name
  - subawardee_parent_uei
  - subawardee_parent_duns
  - subawardee_parent_name
  - subawardee_country_code
  - subawardee_country_name
  - subawardee_address_line_1
  - subawardee_city_name
  - subawardee_state_code
  - subawardee_state_name
  - subawardee_zip_code
  - subaward_recipient_cd_original
  - subaward_recipient_cd_current
  - subawardee_foreign_postal_code
  - subawardee_business_types
  - subaward_primary_place_of_performance_city_name
  - subaward_primary_place_of_performance_state_code
  - subaward_primary_place_of_performance_state_name
  - subaward_primary_place_of_performance_address_zip_code
  - subaward_place_of_performance_cd_original
  - subaward_place_of_performance_cd_current
  - subaward_primary_place_of_performance_country_code
  - subaward_primary_place_of_performance_country_name
  - subaward_description
  - subawardee_highly_compensated_officer_1_name
  - subawardee_highly_compensated_officer_1_amount
  - subawardee_highly_compensated_officer_2_name
  - subawardee_highly_compensated_officer_2_amount
  - subawardee_highly_compensated_officer_3_name
  - subawardee_highly_compensated_officer_3_amount
  - subawardee_highly_compensated_officer_4_name
  - subawardee_highly_compensated_officer_4_amount
  - subawardee_highly_compensated_officer_5_name
  - subawardee_highly_compensated_officer_5_amount
  - usaspending_permalink
  - subaward_sam_report_last_modified_date

## Lato economico: award value
Chiarimento dei campi di importo nei contratti federali (FPDS/USAspending)
1. Cosa rappresenta ciascun campo e a quale fase del contratto si riferisce
base_and_exercised_options_value – Rappresenta il valore attuale del contratto per la parte base più tutte le opzioni già esercitate fino a quel momento
fpds.gov
. In altre parole, indica l’importo del contratto effettivamente messo a valore (obbligato) fino alla data dell’azione corrente. All’aggiudicazione iniziale (contratto base, prima di modifiche), questo campo corrisponde tipicamente al valore iniziale del contratto (la “base”), dato che nessuna opzione è ancora stata esercitata. Ad esempio, se un contratto prevede una base da 10.000 € e opzioni future per 50.000 €, al momento dell’aggiudicazione iniziale base_and_exercised_options_value sarà 10.000 € (ovvero il valore della base)
fedspendingtransparency.github.io
. Man mano che vengono esercitate delle opzioni tramite modifiche, il valore base+opzioni esercitate aumenta: questo campo riflette di volta in volta tale valore corrente del contratto. (In FPDS è anche chiamato “Current Contract Value” – valore corrente del contratto.)
current_total_value_of_award – Questo campo, definito dall’OMB (Office of Management and Budget) nell’ambito dei data standards USAspending, rappresenta il totale attualmente obbligato del contratto fino ad oggi, includendo la base e tutte le opzioni finora esercitate
fedspendingtransparency.github.io
. In pratica è sinonimo del valore attuale complessivo del contratto (corrispondente al concetto di base+opzioni esercitate). È un campo pensato per indicare in modo esplicito il valore totale cumulativo del contratto in un dato momento. Dunque, al momento dell’aggiudicazione iniziale il current_total_value_of_award coincide con la base iniziale (nessuna opzione esercitata ancora), mentre dopo varie modifiche corrisponderà al valore aggiornato dopo l’ultima modifica. Questo data element è stato introdotto per chiarezza nella reportistica della DATA Act, proprio per distinguere i campi cumulativi da quelli relativi alla singola transazione
fedspendingtransparency.github.io
fedspendingtransparency.github.io
.
base_and_all_options_value – Rappresenta il valore totale potenziale del contratto, cioè l’importo massimo concordato se tutte le opzioni venissero esercitate
fpds.gov
. In fase di aggiudicazione iniziale, questo campo equivale al valore contrattuale massimo (“ceiling” o “face value” del contratto) pattuito, sommando la base e tutte le opzioni previste. Riprendendo l’esempio precedente: contratto base 10.000 € con opzioni per 50.000 € avrebbe base_and_all_options_value = 60.000 € al momento dell’aggiudicazione
fedspendingtransparency.github.io
. Questo campo quindi si riferisce al potenziale totale del contratto. Nel contesto della DATA Act/USAspending, esso corrisponde al cosiddetto “Potential Total Value of Award”, definito come l’importo totale che potrebbe essere obbligato se venissero esercitate tutte le opzioni
fedspendingtransparency.github.io
. Durante la vita del contratto, questo valore potenziale può rimanere invariato (se non cambiano le opzioni previste) oppure essere modificato (ad esempio tramite una modifica contrattuale che aggiunge nuove opzioni o aumenta il massimale): in caso di modifiche, come vedremo, il campo viene aggiornato di conseguenza.
2. Ordine cronologico di popolamento e aggiornamento dei campi durante la vita del contratto
All’aggiudicazione iniziale (record iniziale, tipicamente modification_number = 0):
Vengono popolati tutti i valori di base del contratto. In particolare, base_and_exercised_options_value è impostato al valore della base iniziale del contratto (più eventuali opzioni che siano state eccezionalmente già esercitate al momento dell’aggiudicazione)
fpds.gov
. Nella maggior parte dei casi corrisponde semplicemente al valore della base, poiché di norma le opzioni si esercitano successivamente.
Il campo base_and_all_options_value è impostato sin da subito al valore totale potenziale del contratto, cioè la somma di base + tutte le opzioni future previste (l’importo massimo teorico del contratto)
fpds.gov
. Questo valore iniziale rimane come riferimento del “ceiling” contrattuale.
Il current_total_value_of_award in questa fase iniziale coincide concettualmente con il valore base iniziale (dato che nessun altro importo è stato aggiunto). In un eventuale dataset, il record iniziale potrebbe mostrare current_total_value_of_award uguale a base_and_exercised_options_value per l’azione iniziale, riflettendo il fatto che il valore attuale del contratto al momento dell’avvio è pari al valore base. (Analogamente, il potential_total_value_of_award iniziale coincide con base_and_all_options_value, il potenziale massimo iniziale.)
Durante le modifiche successive (record con modification_number > 0):
Aggiornamento incrementale nei campi FPDS: Ogni volta che il contratto subisce una modifica approvata (ad esempio si esercita un’opzione, si aggiunge budget, si riduce scope, ecc.), viene inserito un nuovo record di modifica. In tale record, i campi di valore non ripetono semplicemente il totale contrattuale, ma riportano la variazione apportata da quella modifica:
Nel campo Base and Exercised Options Value dell’azione di modifica si inserisce il cambiamento (positivo o negativo) nel valore corrente del contratto dovuto a quella modifica
fpds.gov
. In altre parole, questo campo sulla modifica indica di quanto aumenta (o diminuisce) il valore “base+opzioni esercitate” a causa di quella specifica azione. Ad esempio, se la modifica consiste nell’esercitare un’opzione da 50.000 €, il record di modifica avrà base_and_exercised_options_value = 50.000 € (incremento). Se la modifica è solo amministrativa senza impatto economico, questo campo sarà 0 € (nessun cambiamento nel valore corrente).
Nel campo Base and All Options Value del record di modifica si inserisce analogamente l’eventuale cambiamento nel valore totale potenziale del contratto dovuto a quella modifica
fpds.gov
. Molte modifiche (ad es. esercitare un’opzione già prevista) non alterano il potenziale totale, perché l’opzione faceva già parte del totale iniziale – in questi casi il base_and_all_options_value sul record di modifica sarà 0 (nessuna variazione al ceiling). Solo modifiche che aggiungono o rimuovono opzioni/valore potenziale faranno avere un importo (positivo o negativo) in questo campo. Ad esempio, una modifica che aggiunge una nuova opzione del valore di 30.000 € (aumentando il ceiling contrattuale) avrà base_and_all_options_value = 30.000 € su quella modifica.
Calcolo dei nuovi totali: FPDS-NG (il sistema gestito da GSA) ricalcola automaticamente i totali cumulativi del contratto man mano che si registrano le modifiche. Le linee guida GSA specificano che per ogni modifica il funzionario deve inserire nel campo “Current” l’importo incrementale, dopodiché “FPDS calcolerà il nuovo totale” per Base and Exercised Options Value e analogamente per Base and All Options Value
acquisition.gov
acquisition.gov
. In pratica, FPDS tiene traccia di due colonne di dati per questi campi: una colonna “Current” (valore immesso per la singola azione) e una colonna “Total” (valore cumulativo risultante)
oig.usaid.gov
. Dunque, cronologicamente, ad ogni nuova modifica i campi “Current” vengono popolati con la variazione e il sistema aggiorna i campi “Total” sommando tale variazione al totale precedente. Ciò garantisce che il valore attuale del contratto e il valore potenziale totale vengano mantenuti aggiornati nel sistema dopo ogni modifica.
Nei dataset USAspending/FPDS: le estrazioni di dati normalmente riportano sia i campi incrementali sia quelli cumulativi. Ad esempio, in USAspending troviamo sia base_and_exercised_options_value (che nei record di modifica è l’importo della modifica) sia current_total_value_of_award (che dovrebbe rappresentare il totale aggiornato a seguito di quella modifica). Idealmente, per ogni record:
current_total_value_of_award dopo una modifica = valore totale del contratto a quel punto (base + opzioni esercitate fino a quel mod),
mentre base_and_exercised_options_value = importo dell’azione stessa.
Un audit federale ha evidenziato l’importanza di distinguere correttamente questi due livelli: i campi FPDS “Current” vs “Total” non vanno confusi. In passato ci sono stati casi in cui, per errore, veniva riportato solo l’importo della modifica invece del totale aggiornato, causando inconsistenze nei dati (ad esempio, una modifica a costo zero erroneamente mostrava totale 0 se si prendeva la colonna sbagliata)
oig.usaid.gov
. Questo sottolinea che, concettualmente, base_and_exercised_options_value è legato alla singola transazione, mentre current_total_value_of_award è un valore cumulativo.
In sintesi, l’ordine cronologico di popolamento è: all’inizio si fissano valore base esercitato e valore potenziale totale; ad ogni modifica si aggiornano questi campi inserendo le variazioni e calcolando i nuovi totali. Di conseguenza, man mano che aumenta il modification_number, il sistema “costruisce” il valore corrente e potenziale del contratto sommando i contributi delle varie modifiche in sequenza.
3. Relazione con il campo modification_number e con le modifiche contrattuali
Il campo modification_number (o semplicemente “Modification Number” nel FPDS) identifica l’ordine delle azioni su un contratto: la convenzione è che “0” indica il contratto base iniziale, mentre i numeri 1, 2, 3, … identificano le successive modifiche (1ª modifica, 2ª modifica, ecc.). Questo si riflette nei valori dei campi finanziari come segue:
Record di base (modification 0): contiene i valori iniziali del contratto. Come detto, base_and_exercised_options_value sul record iniziale è l’importo della base (valore iniziale aggiudicato) e base_and_all_options_value è l’importo totale potenziale contrattuale concordato
fpds.gov
fpds.gov
. Essendo il primo record, questi campi indicano l’intero valore senza dipendenze da record precedenti. Anche current_total_value_of_award in questa fase iniziale riflette lo stesso importo della base (il totale “corrente” coincide col valore iniziale, poiché non ci sono ancora modifiche).
Record di modifica (modification_number > 0): ciascun record di modifica non riporta di nuovo tutto il valore del contratto, bensì solo cosa cambia con quella modifica. Pertanto:
base_and_exercised_options_value sul record di una modifica = valore incrementale (o decremento) aggiunto al valore corrente del contratto da quella modifica
fpds.gov
. Ad esempio, se la Modifica n.1 esercita un’opzione da 50k€, quel record avrà base_and_exercised_options_value = +50.000 € (mentre il valore totale attuale del contratto salirà da, poniamo, 10k a 60k). Se la Modifica n.2 poi aggiunge ulteriori 20k€ di fondi, quel record avrà base_and_exercised_options_value = +20.000 € (e il totale corrente diventerà 80k).
base_and_all_options_value sul record di modifica = eventuale variazione al valore potenziale totale dovuta a quella modifica
fpds.gov
. Nel caso di un’opzione esercitata che era già prevista, questa variazione sarà 0 (il totale potenziale rimane 60k nell’esempio sopra). Se invece la Modifica n.3 aggiungesse una nuova opzione del valore di 30k€ aumentando il massimo contrattuale, quel record avrebbe base_and_all_options_value = +30.000 € e il valore potenziale totale del contratto passerebbe da 60k a 90k.
Il modification_number crescente segna l’ordine temporale in cui avvengono questi cambiamenti: la sequenza dei record (0, 1, 2, …) rappresenta la timeline delle azioni contrattuali. Per conoscere il valore complessivo del contratto dopo una certa modifica, occorre considerare tutti i record fino a quel numero di modifica. Fortunatamente, FPDS calcola e mantiene aggiornato il totale: dopo ogni modifica, il sistema conosce il nuovo totale corrente (“Total Base and Exercised Options Value”) e il nuovo totale potenziale (“Total Base and All Options Value”)
acquisition.gov
acquisition.gov
. Questi totali corrispondono ai campi current_total_value_of_award e potential_total_value_of_award riportati nei dataset della DATA Act. Ad esempio, nel nostro scenario:
Dopo la Modifica 1 (opzione 50k esercitata), current_total_value_of_award diventa 60.000 € (10k base + 50k opzione) e potential_total_value_of_award resta 60.000 € (nessun cambiamento del potenziale).
Dopo la Modifica 2 (+20k funding), current_total_value_of_award sarà 80.000 € e potential_total sempre 60.000 € (ancora non si superava il ceiling originale).
Dopo la Modifica 3 (aggiunta opzione +30k), current_total (se non obbligata subito, rimane 80k finché l’opzione non è esercitata) ma potential_total_value_of_award sale a 90.000 € (nuovo massimale).
Questi valori totali aggiornati sono legati al record della modifica stessa – in genere, un dataset come USAspending include in ogni riga sia l’importo di quell’azione sia i totali attuali dopo quell’azione, come discusso sopra. In FPDS, tali totali sono ottenuti accumulando il valore iniziale e le modifiche (il sistema lo fa automaticamente come “Total” columns)
oig.usaid.gov
.
In sintesi, il modification_number determina come interpretare i campi: “0” indica che i campi mostrano valori iniziali assoluti; “>0” indica che i campi base/all options contengono variazioni e vanno sommati ai precedenti per ottenere il nuovo totale. Il legame è tale che senza conoscere il numero di modifica di un record, si potrebbe confondere un valore incrementale con un totale: per questo modification_number va sempre usato per ricostruire cronologicamente il valore del contratto.
4. Implicazioni e logiche per analisi temporali o di variazione (delta)
Quando si analizzano i dati di contratti nel tempo (ad esempio per valutare quando e di quanto variano i valori, o per prevedere modifiche future), è fondamentale usare correttamente questi campi per evitare errori di interpretazione o bias temporali:
Distinguere valori cumulativi vs incrementali: Come visto, current_total_value_of_award e potential_total_value_of_award sono pensati come valori cumulativi aggiornati a quel punto, mentre i campi base_and_exercised_options_value e base_and_all_options_value nei record di modifica rappresentano il delta (la variazione) introdotta dall’azione. Dunque, per un’analisi delle variazioni per ciascuna modifica, conviene utilizzare direttamente i campi incrementali sui record di modifica (esaminando quanto vale base_and_exercised_options_value in ciascuna modifica, che equivale all’aumento o diminuzione in quell’occasione
fpds.gov
). Al contrario, se si vuole tracciare l’andamento del valore totale del contratto nel tempo, è opportuno utilizzare i campi cumulativi dopo ogni azione – ad esempio, prendere current_total_value_of_award per ogni record (o ricalcolarlo sommando progressivamente i delta) fornirà la serie storica del valore totale attuale del contratto dopo ogni modifica.
Evitare doppi conteggi o confusione: Bisogna fare attenzione a non sommare indiscriminatamente i campi senza tenere conto del loro significato. Ad esempio, non si dovrebbe sommare base_and_exercised_options_value di tutti i record più il valore base, perché così si aggiungerebbe il valore iniziale due volte. In realtà, la somma corretta per ottenere il valore finale è: valore iniziale (base_ex del mod 0) + tutte le variazioni successive (base_and_exercised_options_value di ogni modifica) = valore corrente finale. Se invece si usasse current_total_value_of_award di ogni record e li si sommassero, si otterrebbe un numero privo di senso (in quanto ogni record successivo già incorpora i precedenti). In un’analisi temporale “cumulativa” è dunque preferibile utilizzare direttamente il valore current_total_value_of_award di ciascun record come punto della serie (già cumulato fino a lì), oppure calcolare manualmente la somma cumulata dei delta fino a quel punto – entrambi gli approcci portano allo stesso risultato. Per l’analisi “di delta”, invece, si considerano i singoli incrementi (i delta per modifica).
Attenzione al look-ahead bias (bias temporale): Se si utilizzano questi dati per costruire modelli predittivi (ad esempio, come accennato, un predictor per prevedere quando avverrà una modifica contrattuale), è importante non introdurre informazioni future nel modello. In concreto, il campo current_total_value_of_award dopo una modifica contiene già l’effetto di quella modifica, quindi non sarebbe disponibile prima che la modifica avvenisse. Usarlo come feature per predire la modifica equivarrebbe a un “trucco” temporale (look-ahead bias). Pertanto, per analisi predittive, dovremmo piuttosto utilizzare i valori noti fino a prima di una modifica. Ad esempio, se vogliamo prevedere se nel prossimo trimestre un contratto subirà una modifica, potremo considerare il valore attuale del contratto al momento precedente (che, nel dataset, corrisponde al current_total_value_of_award dell’ultimo record disponibile prima della modifica in questione). Ma non dovremmo includere il current_total_value_of_award aggiornato dopo la modifica stessa, perché quello riflette già l’evento che cerchiamo di prevedere. In altre parole, bisogna allineare temporalmente le feature ai target in modo corretto, usando solo dati disponibili fino a quel momento storico.
Utilizzo per analisi delta: I campi discutessi forniscono una base molto utile per analizzare gli incrementi contrattuali. Si può facilmente calcolare l’entità di ogni modifica guardando al valore in base_and_exercised_options_value su quel record (che, come detto, è proprio il delta di valore)
fpds.gov
. Oppure, in maniera equivalente, si potrebbe fare la differenza tra il current_total_value_of_award di una modifica e quello del record precedente: anche questo darebbe l’incremento apportato (salvo eventuali casi di rounding, etc.). Ad esempio, se un record ha current_total=120k e il precedente aveva 100k, sappiamo che la modifica ha aggiunto 20k (coerente con base_and_exercised=20k su quel record di modifica). Per il valore potenziale, analogamente, la differenza tra potential_total_value_of_award successivo e precedente indica un cambio nel ceiling (e dovrebbe corrispondere al valore nel campo base_and_all_options_value della modifica).
Esempio pratico riepilogativo: Supponiamo un contratto con base iniziale 10.000 € e opzioni per ulteriori 50.000 € possibili. Al momento dell’aggiudicazione (Mod 0) avremo:
base_and_exercised_options_value = 10.000 € (base iniziale),
base_and_all_options_value = 60.000 € (potenziale totale)
fedspendingtransparency.github.io
,
current_total_value_of_award = 10.000 € (valore attuale coincidente col base iniziale),
potential_total_value_of_award = 60.000 € (uguale al potenziale iniziale).
Dopo qualche tempo, viene esercitata un’opzione da 50.000 € tramite una modifica (Mod 1):
sul record di Mod 1, base_and_exercised_options_value = 50.000 € (incremento apportato) e base_and_all_options_value = 0 € (il potenziale contrattuale non cambia, era già 60k);
il sistema FPDS aggiorna il totale: il contratto ora ha un valore corrente di 60.000 € (current_total_value_of_award dopo Mod 1) e il potenziale rimane 60.000 € (potential_total_value_of_award invariato)
acquisition.gov
.
Infine, immaginiamo una Modifica 2 che aggiunge una nuova opzione del valore 40.000 € (estendendo il valore massimo del contratto, ma senza ancora esercitarla):
sul record Mod 2 avremo base_and_exercised_options_value = 0 € (questa modifica in sé non obbliga nuovi fondi immediatamente) e base_and_all_options_value = 40.000 € (aumento del valore potenziale);
FPDS ricalcola: il valore attuale del contratto resta 60.000 € (nessun cambiamento negli obblighi attivi perché l’opzione aggiuntiva non è stata ancora esercitata), mentre il valore potenziale totale sale a 100.000 € (potential_total_value_of_award dopo Mod 2).
Questo esempio illustra come i campi si muovono nella timeline del contratto: gli incrementi sono riportati sulle modifiche e vengono accumulati per dare i totali correnti e potenziali ad ogni step.
In conclusione, per analisi temporali accurate occorre: 1) usare i campi giusti in base a ciò che si sta analizzando (totali vs delta), e 2) rispettare la sequenza temporale dei dati evitando di introdurre informazioni future nel passato. Seguendo queste logiche, i campi base_and_exercised_options_value, current_total_value_of_award e base_and_all_options_value (insieme al relativo potential_total_value_of_award) forniscono un quadro completo dell’evoluzione del valore di un contratto federale dal momento dell’aggiudicazione fino alle successive modifiche, permettendo sia di conoscere il valore attuale vs potenziale sia di calcolare i delta ad ogni modifica in modo corretto.