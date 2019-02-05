
-- Table for storing menus for each week
CREATE TABLE menus (
       id SERIAL PRIMARY KEY,
       added_at TIMESTAMP NOT NULL DEFAULT now(),
       start_date DATE NOT NULL,
       end_date DATE NOT NULL,
       menu JSONB NOT NULL
);
