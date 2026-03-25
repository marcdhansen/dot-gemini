# SurrealDB Skill References

Additional schemas and reference materials for the SurrealDB skill.

---

## ONTO-AEC Table Schemas

### onto_ontology

```sql
DEFINE TABLE onto_ontology SCHEMAFULL;
DEFINE FIELD ontology_id ON onto_ontology TYPE string;
DEFINE FIELD name ON onto_ontology TYPE string;
DEFINE FIELD base_iri ON onto_ontology TYPE string;
DEFINE FIELD description ON onto_ontology TYPE option<string>;
DEFINE FIELD domain ON onto_ontology TYPE string DEFAULT 'general';
DEFINE FIELD source_document_id ON onto_ontology TYPE string;
DEFINE FIELD version ON onto_ontology TYPE string DEFAULT '1.0.0';
DEFINE FIELD created_at ON onto_ontology TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON onto_ontology TYPE datetime DEFAULT time::now();
DEFINE INDEX idx_ontology_id ON onto_ontology FIELDS ontology_id UNIQUE;
```

### onto_concept

```sql
DEFINE TABLE onto_concept SCHEMAFULL;
DEFINE FIELD concept_id ON onto_concept TYPE string;
DEFINE FIELD iri ON onto_concept TYPE string;
DEFINE FIELD label_primary ON onto_concept TYPE string;
DEFINE FIELD label_secondary ON onto_concept TYPE option<string>;
DEFINE FIELD label_lang_primary ON onto_concept TYPE string DEFAULT 'en';
DEFINE FIELD label_lang_secondary ON onto_concept TYPE option<string>;
DEFINE FIELD synonyms ON onto_concept TYPE array DEFAULT [];
DEFINE FIELD definition ON onto_concept TYPE string;
DEFINE FIELD concept_type ON onto_concept TYPE string;
DEFINE FIELD source_section ON onto_concept TYPE string;
DEFINE FIELD source_article ON onto_concept TYPE option<string>;
DEFINE FIELD applicable_occupancy_groups ON onto_concept TYPE array DEFAULT [];
DEFINE FIELD applicable_building_types ON onto_concept TYPE array DEFAULT [];
DEFINE FIELD risk_tier ON onto_concept TYPE option<int>;
DEFINE FIELD compliance_path ON onto_concept TYPE option<string>;
DEFINE FIELD constraint_deontic ON onto_concept TYPE option<string>;
DEFINE FIELD constraint_condition ON onto_concept TYPE option<string>;
DEFINE FIELD extraction_confidence ON onto_concept TYPE option<float>;
DEFINE FIELD requires_review ON onto_concept TYPE bool DEFAULT false;
DEFINE FIELD verified_by_human ON onto_concept TYPE bool DEFAULT false;
DEFINE FIELD is_deprecated ON onto_concept TYPE bool DEFAULT false;
DEFINE FIELD deprecation_note ON onto_concept TYPE option<string>;
DEFINE FIELD parent_class_iri ON onto_concept TYPE option<string>;
DEFINE FIELD created_at ON onto_concept TYPE datetime DEFAULT time::now();
DEFINE INDEX idx_concept_iri ON onto_concept FIELDS iri UNIQUE;
DEFINE INDEX idx_concept_type ON onto_concept FIELDS concept_type;
DEFINE INDEX idx_risk_tier ON onto_concept FIELDS risk_tier;
```

### onto_property

```sql
DEFINE TABLE onto_property SCHEMAFULL;
DEFINE FIELD property_id ON onto_property TYPE string;
DEFINE FIELD iri ON onto_property TYPE string;
DEFINE FIELD label_primary ON onto_property TYPE string;
DEFINE FIELD definition ON onto_property TYPE option<string>;
DEFINE FIELD property_type ON onto_property TYPE string;
DEFINE FIELD domain_concept_iri ON onto_property TYPE option<string>;
DEFINE FIELD range_concept_iri ON onto_property TYPE option<string>;
DEFINE FIELD range_datatype ON onto_property TYPE option<string>;
DEFINE FIELD is_functional ON onto_property TYPE bool DEFAULT false;
DEFINE FIELD is_transitive ON onto_property TYPE bool DEFAULT false;
DEFINE FIELD inverse_property_iri ON onto_property TYPE option<string>;
DEFINE FIELD cardinality_min ON onto_property TYPE option<int>;
DEFINE FIELD cardinality_max ON onto_property TYPE option<int>;
DEFINE FIELD source_section ON onto_property TYPE string;
DEFINE FIELD unit_of_measure ON onto_property TYPE option<string>;
DEFINE INDEX idx_property_iri ON onto_property FIELDS iri UNIQUE;
```

### onto_relationship

```sql
DEFINE TABLE onto_relationship SCHEMAFULL;
DEFINE FIELD from_concept_iri ON onto_relationship TYPE string;
DEFINE FIELD to_concept_iri ON onto_relationship TYPE string;
DEFINE FIELD relation_type ON onto_relationship TYPE string;
DEFINE FIELD confidence ON onto_relationship TYPE float DEFAULT 1.0;
DEFINE FIELD source_section ON onto_relationship TYPE option<string>;
DEFINE FIELD created_at ON onto_relationship TYPE datetime DEFAULT time::now();
DEFINE INDEX idx_from_iri ON onto_relationship FIELDS from_concept_iri;
DEFINE INDEX idx_to_iri ON onto_relationship FIELDS to_concept_iri;
DEFINE INDEX idx_relation_type ON onto_relationship FIELDS relation_type;
```

### onto_job

```sql
DEFINE TABLE onto_job SCHEMAFULL;
DEFINE FIELD job_id ON onto_job TYPE string;
DEFINE FIELD status ON onto_job TYPE string;
DEFINE FIELD ontology_id ON onto_job TYPE string;
DEFINE FIELD job_type ON onto_job TYPE string;
DEFINE FIELD created_at ON onto_job TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON onto_job TYPE datetime DEFAULT time::now();
DEFINE FIELD completed_at ON onto_job TYPE option<datetime>;
DEFINE FIELD error_message ON onto_job TYPE option<string>;
DEFINE INDEX idx_job_id ON onto_job FIELDS job_id UNIQUE;
DEFINE INDEX idx_status ON onto_job FIELDS status;
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SURREALDB_URL` | `http://localhost:8000` | Database URL |
| `SURREALDB_USER` | `root` | Username |
| `SURREALDB_PASS` | `root` | Password |
| `SURREALDB_NS` | `aec` | Ontology namespace |
| `SURREALDB_DB` | `ontology` | Ontology database |
| `SURREALDB_MEMORY_NS` | `aec` | Agent memory namespace |
| `SURREALDB_MEMORY_DB` | `agent_memory` | Agent memory database |
