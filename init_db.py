"""
Database Initialization Script for Bus Reservation System
Executes schema.sql, views.sql, and sample_data.sql cleanly in MySQL.
"""

import os
import re
from pathlib import Path
import mysql.connector
from mysql.connector import Error
from config import Config

BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"

def parse_sql_file(file_path):
    """
    Parses an SQL file into individual executable statements,
    handling DELIMITER changes (e.g. DELIMITER $$ for triggers).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    statements = []
    current_statement = []
    current_delimiter = ";"

    for line in lines:
        stripped = line.strip()
        
        # Check for DELIMITER changes
        if stripped.upper().startswith("DELIMITER"):
            parts = stripped.split()
            if len(parts) >= 2:
                current_delimiter = parts[1]
            continue
        
        # Ignore full-line comments
        if stripped.startswith("--") or stripped.startswith("/*") or not stripped:
            if not current_statement:
                continue

        current_statement.append(line)

        # Check if line ends with the current delimiter
        if stripped.endswith(current_delimiter):
            stmt = "\n".join(current_statement)
            # Remove the delimiter from the end
            if current_delimiter != ";":
                stmt = stmt.rstrip()
                if stmt.endswith(current_delimiter):
                    stmt = stmt[:-len(current_delimiter)]
            else:
                stmt = stmt.rstrip()
                if stmt.endswith(";"):
                    stmt = stmt[:-1]
            stmt = stmt.strip()
            if stmt:
                statements.append(stmt)
            current_statement = []

    if current_statement:
        stmt = "\n".join(current_statement).strip()
        if stmt:
            statements.append(stmt)

    return statements

def run_init():
    print("=" * 60)
    print("Initializing Bus Reservation System Database")
    print(f"Connecting to MySQL at {Config.DB_HOST}:{Config.DB_PORT} as '{Config.DB_USER}'...")
    print("=" * 60)

    try:
        # Initial connection without selecting database (since schema.sql creates it)
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            autocommit=True
        )
        cursor = conn.cursor()

        sql_files = ["schema.sql", "views.sql", "sample_data.sql"]

        for fname in sql_files:
            fpath = SQL_DIR / fname
            if not fpath.exists():
                print(f"Warning: File {fpath} does not exist.")
                continue

            print(f"\n[+] Executing {fname}...")
            statements = parse_sql_file(fpath)
            for i, stmt in enumerate(statements, 1):
                try:
                    cursor.execute(stmt)
                except Error as err:
                    print(f"  [!] Error in {fname} at statement #{i}: {err}")
                    raise err
            print(f"  [OK] Successfully executed {len(statements)} statements from {fname}.")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("Database 'bus_system' created, indexed, triggers attached, and seeded.")
        print("=" * 60)

    except Error as e:
        print(f"\n[ERROR] Failed to initialize database: {e}")
        print("\nPlease verify:")
        print("1. MySQL Server is installed and running.")
        print("2. The credentials in your .env file match your MySQL setup.")
        print("3. User has privileges to CREATE DATABASE and CREATE TRIGGER.")

if __name__ == "__main__":
    run_init()
