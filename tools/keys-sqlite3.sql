PRAGMA foreign_keys = ON;

CREATE TABLE members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,  
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(100)
);

CREATE TABLE keys (
    key_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_type VARCHAR(50) NOT NULL,  
    key_number VARCHAR(50),
    uid VARCHAR(50) UNIQUE,  
    transponder_number VARCHAR(50) UNIQUE,  
    access_area TEXT NOT NULL,  
    programmed_by INT,  
    programmed_at TEXT,
    extra TEXT,  
    FOREIGN KEY (programmed_by) REFERENCES members(member_id)
);

CREATE TABLE key_assignments (
    key_id INTEGER PRIMARY KEY AUTOINCREMENT,  
    member_id INT NOT NULL,  
    assigned_at TEXT NOT NULL,  
    loaned_by INT NOT NULL,  
    deposit DECIMAL(10,2) DEFAULT 0.00,  
    remark TEXT,  
    FOREIGN KEY (key_id) REFERENCES keys(key_id),  
    FOREIGN KEY (member_id) REFERENCES members(member_id),  
    FOREIGN KEY (loaned_by) REFERENCES members(member_id)
);

CREATE TABLE key_verifications (
    verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id INT NOT NULL,
    verified_by INT NOT NULL,
    verified_at TEXT NOT NULL,
    remark TEXT,
    FOREIGN KEY (key_id) REFERENCES keys(key_id),
    FOREIGN KEY (verified_by) REFERENCES members(member_id)
);

CREATE TABLE accounting (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,  
    member_first_name VARCHAR(100) NOT NULL,    -- Mitglied, das Pfand zahlt/bekommt 
    member_last_name VARCHAR(100) NOT NULL,    -- Mitglied, das Pfand zahlt/bekommt
    key_id INTEGER,  -- Falls Pfand mit einem Schlüssel verbunden ist  
    amount DECIMAL(10,2) NOT NULL,  
    entry_type VARCHAR(10) NOT NULL,  -- 'deposit' (Pfand gezahlt) oder 'refund' (Pfand zurück)  
    entry_date TEXT DEFAULT (datetime('now', 'localtime')),  
    remark VARCHAR(255),   
    FOREIGN KEY (key_id) REFERENCES keys(key_id)
);
CREATE TABLE key_returns (
    return_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id INT NOT NULL,  -- Referenz zum Schlüssel, der zurückgegeben wurde
    member_id INT NOT NULL,  -- Das Mitglied, das den Schlüssel zurückgibt
    assigned_at TEXT NOT NULL,
    loaned_by INT NOT NULL,     -- Die Person, die die Ausgabe verifiziert hat
    returned_at TEXT NOT NULL,  -- Datum und Uhrzeit der Rückgabe
    returned_by INT NOT NULL,  -- Die Person, die die Rückgabe verifiziert hat
    return_reason TEXT,  -- Optionaler Grund für die Rückgabe
    remark TEXT,  -- Optionaler Kommentar zu dieser Rückgabe
    FOREIGN KEY (key_id) REFERENCES keys(key_id),  -- Verweis auf den Schlüssel
    FOREIGN KEY (member_id) REFERENCES members(member_id),  -- Verweis auf das Mitglied
    FOREIGN KEY (returned_by) REFERENCES members(member_id)  -- Verweis auf den Herausgber*in
);