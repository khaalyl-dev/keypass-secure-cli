"""
keypass - Minimal Secure CLI Demo

A secure CLI application that stores encrypted credentials and device information
in a MongoDB database. Uses OS keyring for master key storage and Fernet encryption
for credential security.

Features:
- Encrypted credential storage with per-user isolation
- Device registration and management
- OS keyring integration for master key storage
- MongoDB Atlas cloud database (benananekhalilo_db_user)
"""

import os
import sys
import datetime
import getpass
import base64
import json
import typer
from typing import Optional, List
from pymongo import MongoClient
from cryptography.fernet import Fernet
import keyring
from bson import ObjectId

# Initialize the Typer CLI application
app = typer.Typer(help="keypass — minimal secure CLI demo (test only)")

# =============================================================================
# DATABASE CONNECTION CONFIGURATION
# =============================================================================

def _get_mongodb_connection():
    """
    Establish MongoDB connection using the benananekhalilo_db_user database.
    
    This function creates a connection to the MongoDB Atlas cloud database
    using hardcoded credentials. It's designed to be simple and reliable
    without requiring environment variable configuration.
    
    Returns:
        MongoClient: Connected MongoDB client instance
        
    Raises:
        typer.Exit: If connection fails, exits with error code 1
    """
    
    # Hardcoded database credentials for benananekhalilo_db_user
    # These credentials provide access to the shared cloud database
    atlas_user = "benananekhalilo_db_user"      # Database username
    atlas_pass = "vUMZOj5VO5RwAxGL"            # Database password
    atlas_cluster = "keypass.kq91w0b"          # MongoDB Atlas cluster name
    
    try:
        # Construct MongoDB Atlas connection URI
        # Format: mongodb+srv://username:password@cluster.mongodb.net/
        uri = f"mongodb+srv://{atlas_user}:{atlas_pass}@{atlas_cluster}.mongodb.net/"
        
        # Create MongoDB client and test connection
        client = MongoClient(uri)
        client.admin.command('ping')  # Test connection with ping command
        
        return client
        
    except Exception as e:
        # Handle connection failures with helpful error messages
        typer.echo("❌ Could not connect to benananekhalilo_db_user database!")
        typer.echo("")
        typer.echo("Error details:")
        typer.echo(f"  {e}")
        typer.echo("")
        typer.echo("Troubleshooting:")
        typer.echo("1. Check your internet connection")
        typer.echo("2. Verify the database is accessible")
        typer.echo("")
        raise typer.Exit(code=1)

# =============================================================================
# DATABASE INITIALIZATION AND CONFIGURATION
# =============================================================================

# Initialize MongoDB connection at module load time
# This allows for early connection testing and database setup
try:
    _client = _get_mongodb_connection()
    DB_NAME = os.getenv("KEYPASS_DB_NAME", "keypass_db")  # Default database name
    DB = _client[DB_NAME]  # Get database instance
except Exception:
    # If initial connection fails, set DB to None
    # Connection will be retried when first command is executed
    DB = None

def _ensure_db_connection():
    """
    Ensure we have a valid database connection.
    
    This function is called before any database operation to guarantee
    that we have an active connection. If the connection is None or
    has been lost, it will attempt to reconnect.
    
    Raises:
        typer.Exit: If connection cannot be established
    """
    global DB
    if DB is None:
        try:
            _client = _get_mongodb_connection()
            DB_NAME = os.getenv("KEYPASS_DB_NAME", "keypass_db")
            DB = _client[DB_NAME]
            _init_db_indexes()  # Set up database indexes
        except Exception:
            raise typer.Exit(code=1)

def _init_db_indexes() -> None:
    """
    Initialize database indexes for optimal performance.
    
    Creates indexes to ensure:
    1. Unique credential names per user (prevents duplicates)
    2. Efficient device listing by registration time
    """
    try:
        # Create unique index for credentials per user
        # This prevents duplicate credential names for the same user
        DB.items.create_index(
            [("type", 1), ("user", 1), ("name", 1)],  # Compound index
            unique=True,                               # Enforce uniqueness
            name="uniq_credential_per_user"
        )
        
        # Create index for efficient device listing by registration time
        # -1 means descending order (newest first)
        DB.devices.create_index(
            [("registered_at", -1)], 
            name="devices_registered_at_desc"
        )
    except Exception:
        # Index creation errors shouldn't break CLI functionality
        # This allows the app to work even if index creation fails
        pass

# =============================================================================
# ENCRYPTION AND KEYRING CONFIGURATION
# =============================================================================

# Keyring configuration for storing the master encryption key
# The keyring service stores the master key securely in the OS keyring
KEYRING_SERVICE = "keypass"      # Service name for keyring storage
KEYRING_KEYNAME = "master_key"   # Key name within the service

def _get_fernet():
    """
    Get the Fernet encryption object using the master key from keyring.
    
    This function retrieves the master encryption key from the OS keyring
    and creates a Fernet cipher object for encrypting/decrypting credentials.
    
    Returns:
        Fernet: Fernet cipher object for encryption/decryption
        
    Raises:
        typer.Exit: If master key is not found in keyring
    """
    # Retrieve the master key from OS keyring
    key = keyring.get_password(KEYRING_SERVICE, KEYRING_KEYNAME)
    if not key:
        typer.echo("No master key found. Run: keypass init")
        raise typer.Exit(code=1)
    
    # Create Fernet cipher object with the master key
    return Fernet(key.encode())

# =============================================================================
# CLI COMMANDS - INITIALIZATION
# =============================================================================

@app.command()
def init(reset: bool = typer.Option(False, help="Reset existing key if present")):
    """
    Initialize the app by generating and saving a master key in the OS keyring.
    
    This command is required before using any other commands. It generates
    a secure master encryption key and stores it in the OS keyring for
    encrypting/decrypting credentials.
    
    Args:
        reset: If True, overwrite existing master key
    """
    # Check if master key already exists
    existing = keyring.get_password(KEYRING_SERVICE, KEYRING_KEYNAME)
    if existing and not reset:
        typer.echo("Master key already exists. Use --reset to overwrite.")
        raise typer.Exit()
    
    # Generate a new Fernet encryption key
    key = Fernet.generate_key().decode()
    
    # Store the master key securely in OS keyring
    keyring.set_password(KEYRING_SERVICE, KEYRING_KEYNAME, key)
    
    typer.echo("✅ Master key generated and stored in OS keyring.")

@app.command()
def export_master_key(
    file_path: str = typer.Argument(..., help="File path to save the master key"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
):
    """
    Export the master key to a file for backup or transfer to another PC.
    
    WARNING: This exports your master key in plain text. Store the file securely!
    The master key allows access to all your encrypted credentials.
    
    Args:
        file_path: Path where to save the master key file
        force: Overwrite existing file without confirmation
    """
    # Check if master key exists
    key = keyring.get_password(KEYRING_SERVICE, KEYRING_KEYNAME)
    if not key:
        typer.echo("❌ No master key found. Run: keypass init")
        raise typer.Exit(code=1)
    
    # Check if file already exists
    if os.path.exists(file_path) and not force:
        typer.echo(f"❌ File '{file_path}' already exists. Use --force to overwrite.")
        raise typer.Exit(code=1)
    
    try:
        # Write master key to file
        with open(file_path, 'w') as f:
            f.write(key)
        
        # Set secure file permissions (readable only by owner)
        os.chmod(file_path, 0o600)
        
        typer.echo(f"✅ Master key exported to: {file_path}")
        typer.echo("")
        typer.echo("⚠️  SECURITY WARNING:")
        typer.echo("  - Store this file securely (encrypted drive, password manager)")
        typer.echo("  - Delete the file after importing to other PCs")
        typer.echo("  - Anyone with this file can access your credentials")
        
    except Exception as e:
        typer.echo(f"❌ Failed to export master key: {e}")
        raise typer.Exit(code=1)

@app.command()
def import_master_key(
    file_path: str = typer.Argument(..., help="File path containing the master key"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing master key"),
):
    """
    Import a master key from a file to restore access to credentials.
    
    This allows you to use the same master key across multiple PCs,
    giving you access to your encrypted credentials on any device.
    
    Args:
        file_path: Path to the master key file
        force: Overwrite existing master key without confirmation
    """
    # Check if file exists
    if not os.path.exists(file_path):
        typer.echo(f"❌ File not found: {file_path}")
        raise typer.Exit(code=1)
    
    # Check if master key already exists
    existing_key = keyring.get_password(KEYRING_SERVICE, KEYRING_KEYNAME)
    if existing_key and not force:
        typer.echo("❌ Master key already exists. Use --force to overwrite.")
        typer.echo("⚠️  WARNING: This will make existing credentials inaccessible!")
        raise typer.Exit(code=1)
    
    try:
        # Read master key from file
        with open(file_path, 'r') as f:
            key = f.read().strip()
        
        # Validate the key format (Fernet keys are base64 encoded, 44 characters)
        if len(key) != 44:
            typer.echo("❌ Invalid master key format.")
            raise typer.Exit(code=1)
        
        # Test the key by creating a Fernet object
        try:
            Fernet(key.encode())
        except Exception:
            typer.echo("❌ Invalid master key format.")
            raise typer.Exit(code=1)
        
        # Store the master key in keyring
        keyring.set_password(KEYRING_SERVICE, KEYRING_KEYNAME, key)
        
        typer.echo("✅ Master key imported successfully!")
        typer.echo("")
        typer.echo("🔓 You now have access to your encrypted credentials.")
        typer.echo("💡 Tip: Delete the master key file for security.")
        
    except Exception as e:
        typer.echo(f"❌ Failed to import master key: {e}")
        raise typer.Exit(code=1)

@app.command()
def backup_credentials(
    file_path: str = typer.Argument(..., help="File path to save the backup"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
):
    """
    Create a complete backup of all credentials and the master key.
    
    This creates a secure backup that can be restored on any PC.
    The backup includes both credentials and the master key.
    
    Args:
        file_path: Path where to save the backup file
        force: Overwrite existing file without confirmation
    """
    _ensure_db_connection()
    
    # Check if file already exists
    if os.path.exists(file_path) and not force:
        typer.echo(f"❌ File '{file_path}' already exists. Use --force to overwrite.")
        raise typer.Exit(code=1)
    
    # Get master key
    master_key = keyring.get_password(KEYRING_SERVICE, KEYRING_KEYNAME)
    if not master_key:
        typer.echo("❌ No master key found. Run: keypass init")
        raise typer.Exit(code=1)
    
    try:
        # Get all credentials for current user
        owner = getpass.getuser().strip()
        credentials = list(DB.items.find({"type": "credential", "user": owner}))
        
        # Create backup data
        backup_data = {
            "version": "1.0",
            "created_at": datetime.datetime.utcnow().isoformat(),
            "user": owner,
            "master_key": master_key,
            "credentials": []
        }
        
        # Add credentials to backup
        for cred in credentials:
            backup_data["credentials"].append({
                "name": cred["name"],
                "token": cred["token"],  # Already encrypted
                "tags": cred.get("tags", []),
                "created_at": cred["created_at"].isoformat()
            })
        
        # Write backup to file
        with open(file_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        # Set secure file permissions
        os.chmod(file_path, 0o600)
        
        typer.echo(f"✅ Backup created: {file_path}")
        typer.echo(f"📊 Credentials backed up: {len(credentials)}")
        typer.echo("")
        typer.echo("⚠️  SECURITY WARNING:")
        typer.echo("  - Store this backup securely")
        typer.echo("  - Delete the backup file after restoring")
        typer.echo("  - Anyone with this file can access your credentials")
        
    except Exception as e:
        typer.echo(f"❌ Failed to create backup: {e}")
        raise typer.Exit(code=1)

@app.command()
def restore_credentials(
    file_path: str = typer.Argument(..., help="File path containing the backup"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing credentials"),
):
    """
    Restore credentials from a backup file.
    
    This restores both the master key and all credentials from a backup
    created with the backup-credentials command.
    
    Args:
        file_path: Path to the backup file
        force: Overwrite existing credentials without confirmation
    """
    _ensure_db_connection()
    
    # Check if file exists
    if not os.path.exists(file_path):
        typer.echo(f"❌ File not found: {file_path}")
        raise typer.Exit(code=1)
    
    # Check if credentials already exist
    owner = getpass.getuser().strip()
    existing_creds = DB.items.count_documents({"type": "credential", "user": owner})
    if existing_creds > 0 and not force:
        typer.echo(f"❌ Found {existing_creds} existing credentials. Use --force to overwrite.")
        raise typer.Exit(code=1)
    
    try:
        # Read backup file
        with open(file_path, 'r') as f:
            backup_data = json.load(f)
        
        # Validate backup format
        if "version" not in backup_data or "master_key" not in backup_data:
            typer.echo("❌ Invalid backup file format.")
            raise typer.Exit(code=1)
        
        # Import master key
        keyring.set_password(KEYRING_SERVICE, KEYRING_KEYNAME, backup_data["master_key"])
        
        # Delete existing credentials if force is used
        if force and existing_creds > 0:
            DB.items.delete_many({"type": "credential", "user": owner})
            typer.echo(f"🗑️  Removed {existing_creds} existing credentials")
        
        # Restore credentials
        restored_count = 0
        for cred_data in backup_data.get("credentials", []):
            doc = {
                "type": "credential",
                "name": cred_data["name"],
                "user": owner,
                "token": cred_data["token"],
                "tags": cred_data.get("tags", []),
                "created_at": datetime.datetime.fromisoformat(cred_data["created_at"])
            }
            DB.items.insert_one(doc)
            restored_count += 1
        
        typer.echo(f"✅ Restored {restored_count} credentials")
        typer.echo("🔓 Master key imported - you can now access your credentials")
        
    except Exception as e:
        typer.echo(f"❌ Failed to restore backup: {e}")
        raise typer.Exit(code=1)

# =============================================================================
# CLI COMMANDS - CREDENTIAL MANAGEMENT
# =============================================================================

@app.command()
def add_cred(
    name: str,
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Username owner of this credential (defaults to OS user)"),
):
    """
    Add an encrypted credential. You will be prompted for the secret.
    
    This command stores a credential securely by:
    1. Prompting for the secret (hidden input)
    2. Encrypting the secret with the master key
    3. Storing the encrypted credential in the database
    4. Associating it with a specific user (for isolation)
    
    Args:
        name: Name/identifier for the credential
        tags: Optional tags for categorizing the credential
        user: Username owner (defaults to current OS user)
    """
    # Ensure database connection is available
    _ensure_db_connection()
    
    # Prompt for secret with hidden input (getpass)
    secret = getpass.getpass(f"Secret for '{name}': ")
    if not secret:
        typer.echo("Empty secret — aborting.")
        raise typer.Exit()

    # Get Fernet cipher for encryption
    f = _get_fernet()
    
    # Determine credential owner (default to OS user)
    owner = (user or getpass.getuser()).strip()
    
    # Encrypt the secret using Fernet
    token = f.encrypt(secret.encode())
    
    # Create document for database storage
    doc = {
        "type": "credential",                           # Document type identifier
        "name": name,                                   # Credential name
        "user": owner,                                  # Owner for user isolation
        "token": base64.b64encode(token).decode(),     # Base64 encoded encrypted secret
        "tags": tags or [],                            # Optional tags
        "created_at": datetime.datetime.utcnow()       # Timestamp
    }
    
    # Store in database and return confirmation
    result = DB.items.insert_one(doc)
    typer.echo(f"Saved credential '{name}' (id: {result.inserted_id})")

@app.command()
def get_cred(
    name: str,
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Username owner of the credential (defaults to OS user)"),
):
    """
    Retrieve and decrypt a credential by name (for testing).
    
    This command retrieves a stored credential and decrypts it using the
    master key. The decrypted secret is displayed in plain text.
    
    WARNING: This command displays secrets in plain text. Use with caution
    in production environments.
    
    Args:
        name: Name of the credential to retrieve
        user: Username owner (defaults to current OS user)
    """
    # Ensure database connection is available
    _ensure_db_connection()
    
    # Determine credential owner
    owner = (user or getpass.getuser()).strip()
    
    # Find the credential in the database
    doc = DB.items.find_one({"type": "credential", "user": owner, "name": name})
    if not doc:
        typer.echo("❌ Credential not found.")
        raise typer.Exit(code=1)
    
    # Decode the base64 encoded encrypted token
    token = base64.b64decode(doc["token"])
    
    # Get Fernet cipher for decryption
    f = _get_fernet()
    
    try:
        # Decrypt the secret using Fernet
        plaintext = f.decrypt(token).decode()
    except Exception as e:
        typer.echo("❌ Failed to decrypt secret: " + str(e))
        raise typer.Exit(code=1)
    
    # Display the decrypted secret
    typer.echo(f"🔓 {name}: {plaintext}")

@app.command()
def delete_cred(
    name: str,
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Username owner of the credential (defaults to OS user)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """
    Delete a credential by name.
    
    This command permanently removes a credential from the database.
    By default, it asks for confirmation before deletion to prevent
    accidental data loss.
    
    Args:
        name: Name of the credential to delete
        user: Username owner (defaults to current OS user)
        force: Skip confirmation prompt (use with caution)
    """
    # Ensure database connection is available
    _ensure_db_connection()
    
    # Determine credential owner
    owner = (user or getpass.getuser()).strip()
    
    # Check if credential exists
    doc = DB.items.find_one({"type": "credential", "user": owner, "name": name})
    if not doc:
        typer.echo("❌ Credential not found.")
        raise typer.Exit(code=1)
    
    # Ask for confirmation unless --force is used
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete credential '{name}' for user '{owner}'?")
        if not confirm:
            typer.echo("❌ Deletion cancelled.")
            raise typer.Exit()
    
    # Delete the credential from database
    result = DB.items.delete_one({"type": "credential", "user": owner, "name": name})
    if result.deleted_count > 0:
        typer.echo(f"✅ Credential '{name}' deleted successfully.")
    else:
        typer.echo("❌ Failed to delete credential.")
        raise typer.Exit(code=1)

# =============================================================================
# CLI COMMANDS - DEVICE MANAGEMENT
# =============================================================================

@app.command()
def add_device(mac: str, ip: str, hostname: Optional[str] = typer.Argument(None)):
    """
    Register a device with mac and ip.
    
    This command stores device information in the database for tracking
    and management purposes. Device information is stored unencrypted
    as it's not sensitive data.
    
    Args:
        mac: MAC address of the device (will be converted to lowercase)
        ip: IP address of the device
        hostname: Optional hostname/name for the device
    """
    # Ensure database connection is available
    _ensure_db_connection()
    
    # Create device document for database storage
    doc = {
        "type": "device",                           # Document type identifier
        "mac": mac.lower(),                         # MAC address (normalized to lowercase)
        "ip": ip,                                   # IP address
        "hostname": hostname or "",                 # Optional hostname
        "registered_at": datetime.datetime.utcnow() # Registration timestamp
    }
    
    # Store device in database and return confirmation
    result = DB.devices.insert_one(doc)
    typer.echo(f"Device registered (id: {result.inserted_id})")

@app.command()
def list_devices():
    """
    List registered devices.
    
    This command displays all registered devices in the database,
    sorted by registration time (newest first). Shows device ID,
    MAC address, IP address, hostname, and registration timestamp.
    """
    # Ensure database connection is available
    _ensure_db_connection()
    
    # Query devices sorted by registration time (newest first)
    cursor = DB.devices.find().sort("registered_at", -1)
    rows = list(cursor)
    
    # Check if any devices exist
    if not rows:
        typer.echo("No devices registered.")
        return
    
    # Display each device with its information
    for d in rows:
        rid = str(d.get("_id"))           # Device ID (MongoDB ObjectId)
        mac = d.get("mac")                # MAC address
        ip = d.get("ip")                  # IP address
        hs = d.get("hostname", "")        # Hostname (empty string if not set)
        ts = d.get("registered_at")       # Registration timestamp
        
        # Format and display device information
        typer.echo(f"- id={rid} mac={mac} ip={ip} hostname={hs} registered_at={ts}")

@app.command()
def remove_device(
    device_id: str,
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """
    Remove a device by its ID.
    
    This command permanently removes a device from the database.
    By default, it asks for confirmation before deletion to prevent
    accidental data loss. The device ID can be found using list-devices.
    
    Args:
        device_id: MongoDB ObjectId of the device to remove
        force: Skip confirmation prompt (use with caution)
    """
    # Ensure database connection is available
    _ensure_db_connection()
    
    try:
        # Convert string ID to MongoDB ObjectId
        from bson import ObjectId
        device_object_id = ObjectId(device_id)
    except Exception:
        typer.echo("❌ Invalid device ID format.")
        raise typer.Exit(code=1)
    
    # Check if device exists
    doc = DB.devices.find_one({"_id": device_object_id})
    if not doc:
        typer.echo("❌ Device not found.")
        raise typer.Exit(code=1)
    
    # Ask for confirmation unless --force is used
    if not force:
        mac = doc.get("mac", "unknown")
        ip = doc.get("ip", "unknown")
        hostname = doc.get("hostname", "no hostname")
        confirm = typer.confirm(f"Are you sure you want to remove device {mac} ({ip}) - {hostname}?")
        if not confirm:
            typer.echo("❌ Removal cancelled.")
            raise typer.Exit()
    
    # Delete the device from database
    result = DB.devices.delete_one({"_id": device_object_id})
    if result.deleted_count > 0:
        typer.echo(f"✅ Device {device_id} removed successfully.")
    else:
        typer.echo("❌ Failed to remove device.")
        raise typer.Exit(code=1)

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Run the CLI application when script is executed directly
    app()
