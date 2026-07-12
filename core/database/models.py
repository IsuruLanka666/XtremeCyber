"""
SQLite database schema for XtremeCyber.
"""

from core.constants import DATABASE_SCHEMA_VERSION, DEFAULT_SETTINGS


CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS schema_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email TEXT UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer'
        CHECK (role IN ('admin', 'analyst', 'viewer')),
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_login_at TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL,
    scan_type TEXT NOT NULL,
    port_range TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (
            status IN (
                'pending',
                'running',
                'completed',
                'failed',
                'cancelled'
            )
        ),
    started_at TEXT,
    completed_at TEXT,
    duration_seconds REAL,
    hosts_discovered INTEGER NOT NULL DEFAULT 0,
    open_ports INTEGER NOT NULL DEFAULT 0,
    vulnerabilities_found INTEGER NOT NULL DEFAULT 0,
    critical_count INTEGER NOT NULL DEFAULT 0,
    high_count INTEGER NOT NULL DEFAULT 0,
    medium_count INTEGER NOT NULL DEFAULT 0,
    low_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    ip_address TEXT NOT NULL,
    hostname TEXT,
    mac_address TEXT,
    vendor TEXT,
    operating_system TEXT,
    os_accuracy INTEGER,
    status TEXT NOT NULL DEFAULT 'unknown'
        CHECK (status IN ('unknown', 'online', 'offline')),
    response_time_ms REAL,
    created_at TEXT NOT NULL,
    UNIQUE(scan_id, ip_address),
    FOREIGN KEY (scan_id)
        REFERENCES scan_history(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id INTEGER NOT NULL,
    port_number INTEGER NOT NULL
        CHECK (port_number BETWEEN 1 AND 65535),
    protocol TEXT NOT NULL DEFAULT 'tcp'
        CHECK (protocol IN ('tcp', 'udp')),
    state TEXT NOT NULL DEFAULT 'unknown'
        CHECK (
            state IN (
                'open',
                'closed',
                'filtered',
                'unknown'
            )
        ),
    service_name TEXT,
    product TEXT,
    version TEXT,
    banner TEXT,
    extra_info TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(host_id, port_number, protocol),
    FOREIGN KEY (host_id)
        REFERENCES hosts(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    host_id INTEGER,
    port_id INTEGER,
    cve_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL DEFAULT 'informational'
        CHECK (
            severity IN (
                'informational',
                'low',
                'medium',
                'high',
                'critical'
            )
        ),
    cvss_score REAL
        CHECK (
            cvss_score IS NULL
            OR cvss_score BETWEEN 0 AND 10
        ),
    affected_component TEXT,
    recommendation TEXT,
    reference_url TEXT,
    detected_at TEXT NOT NULL,
    FOREIGN KEY (scan_id)
        REFERENCES scan_history(id)
        ON DELETE CASCADE,
    FOREIGN KEY (host_id)
        REFERENCES hosts(id)
        ON DELETE CASCADE,
    FOREIGN KEY (port_id)
        REFERENCES ports(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    report_type TEXT NOT NULL
        CHECK (report_type IN ('pdf', 'csv', 'json')),
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (scan_id)
        REFERENCES scan_history(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS app_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    level TEXT NOT NULL,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    details TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_scan_history_target
    ON scan_history(target);

CREATE INDEX IF NOT EXISTS idx_scan_history_status
    ON scan_history(status);

CREATE INDEX IF NOT EXISTS idx_scan_history_created_at
    ON scan_history(created_at);

CREATE INDEX IF NOT EXISTS idx_hosts_scan_id
    ON hosts(scan_id);

CREATE INDEX IF NOT EXISTS idx_ports_host_id
    ON ports(host_id);

CREATE INDEX IF NOT EXISTS idx_vulnerabilities_scan_id
    ON vulnerabilities(scan_id);

CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity
    ON vulnerabilities(severity);

CREATE INDEX IF NOT EXISTS idx_reports_scan_id
    ON reports(scan_id);
"""


def schema_metadata_values() -> dict[str, str]:
    """Return metadata that must exist after initialization."""

    return {
        "schema_version": str(DATABASE_SCHEMA_VERSION),
        "application": "XtremeCyber",
    }


def default_setting_values() -> dict[str, str]:
    """Return the default application settings."""

    return DEFAULT_SETTINGS.copy()