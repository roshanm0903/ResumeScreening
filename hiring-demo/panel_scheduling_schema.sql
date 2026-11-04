-- Prepared for production working-hours constraints; unused by demo scheduling.
CREATE TABLE IF NOT EXISTS panel_members (
 id INTEGER PRIMARY KEY,
 display_name TEXT NOT NULL,
 time_zone TEXT NOT NULL -- IANA zone, e.g. Asia/Kolkata; validate on ingestion.
);
CREATE TABLE IF NOT EXISTS role_panel_members (
 role_id INTEGER NOT NULL REFERENCES roles(id),
 panel_member_id INTEGER NOT NULL REFERENCES panel_members(id),
 PRIMARY KEY (role_id, panel_member_id)
);
CREATE TABLE IF NOT EXISTS panel_working_hours (
 panel_member_id INTEGER NOT NULL REFERENCES panel_members(id),
 weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6), -- Monday=0.
 start_minute INTEGER NOT NULL CHECK (start_minute BETWEEN 0 AND 1439),
 end_minute INTEGER NOT NULL CHECK (end_minute BETWEEN 1 AND 1440),
 CHECK (start_minute < end_minute), -- Local wall-clock minutes; split overnight windows.
 PRIMARY KEY (panel_member_id, weekday, start_minute, end_minute)
);
