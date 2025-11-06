# PostgreSQL Database Setup for Avaliar

## Docker Command

To run PostgreSQL with Docker:

```bash
docker run --name postgres-avaliar -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:latest
```

## Connection Command
```bash
psql -h localhost -p 5432 -U postgres
```

## Database Creation
```sql
CREATE DATABASE avaliar;
```

## User Creation

```sql
-- Create a dedicated user for the application
CREATE ROLE avaliador LOGIN PASSWORD 'passwd';

-- Assign ownership of the database to the new user
ALTER DATABASE avaliar OWNER TO avaliador;
```

## Table Creation Schema

```sql
-- Provas (exams/tests) table
CREATE TABLE provas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trigger function to update modified_at timestamp
CREATE OR REPLACE FUNCTION update_modified_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the trigger to provas table
CREATE TRIGGER update_provas_modified_at
    BEFORE UPDATE ON provas
    FOR EACH ROW EXECUTE FUNCTION update_modified_at_column();
```

## Additional Setup Steps

1. Ensure PostgreSQL is installed and running on your system
2. The application currently uses file-based storage (not database), but if database integration is added in the future, you may need to:
   - Create tables based on the models in `app/models/`
   - Configure database connection in `.env` file
   - Install database dependencies (SQLAlchemy, psycopg2, etc.)

## Notes
- The current implementation stores data as files in the `static/latex_sources` directory
- No database tables are required for the current version of the application
- Future versions may implement database persistence