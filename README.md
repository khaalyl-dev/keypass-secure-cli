# keypass — minimal secure CLI demo (test only)

This is a small demo CLI you can install locally and use to test encrypted storage with MongoDB.

**NOT production-ready.** Intended for quick testing.

## 🚀 Quick Start for Users

### Step 1: Install
```bash
pip install keypass-secure-cli
```

### Step 2: Initialize & Use (Zero Setup!)
```bash
keypass init
keypass add-cred github_token
keypass get-cred github_token
keypass add-device aa:bb:cc:dd:ee:ff 192.168.1.100 my-laptop
keypass list-devices
keypass delete-cred github_token
keypass remove-device <device-id>
```

**That's it!** The app automatically connects to our secure cloud database.

### 🔧 Advanced Setup (Optional)

**Use Your Own Atlas Database:**
```bash
export MONGO_ATLAS_USER="your_username"
export MONGO_ATLAS_PASS="your_password"
export MONGO_ATLAS_CLUSTER="your_cluster_name"
```

**Use Local MongoDB:**
```bash
brew install mongodb-community  # macOS
brew services start mongodb-community
```

### 🎯 Quick Setup Script
```bash
# Run the interactive setup script
./quick_setup.sh
```

## Warnings & next steps

This demo stores secrets in MongoDB encrypted with a symmetric key stored in your OS keyring. For production:

- Use KMS (AWS KMS / GCP KMS / HashiCorp Vault) or a secure HSM.
- Add authentication and audit logging.
- Rotate keys, protect logs, and never print secrets in plain text.
