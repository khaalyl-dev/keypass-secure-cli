# MyApp User Guide

## 🚀 Quick Start for New Users

When you install `myapp-secure-cli`, here's exactly what you need to do:

### Step 1: Install the App
```bash
# Install from PyPI (when published)
pip install myapp-secure-cli

# OR install from local package
pip install dist/myapp-secure-cli-0.1.0-py3-none-any.whl
```

### Step 2: Initialize & Use (Zero Setup!)
```bash
myapp init
myapp add-cred github_token
myapp get-cred github_token
myapp add-device aa:bb:cc:dd:ee:ff 192.168.1.100 my-laptop
myapp list-devices
```

**That's it!** The app automatically connects to our secure cloud database. No environment variables needed!

### 🔧 Advanced Database Setup (Optional)

You have **3 options** if you want to use a different database:

#### Option A: Use Our Cloud Database (Default) ⭐
**No setup required!** The app automatically uses our secure cloud database.

#### Option B: Use Your Own MongoDB Atlas
1. Create free account at https://cloud.mongodb.com
2. Create a cluster and database user
3. Set your own environment variables:

```bash
export MONGO_ATLAS_USER="your_username"
export MONGO_ATLAS_PASS="your_password"
export MONGO_ATLAS_CLUSTER="your_cluster_name"
```

#### Option C: Use Local MongoDB
```bash
# Install MongoDB locally
brew install mongodb-community  # macOS
brew services start mongodb-community

# No environment variables needed - app will connect automatically
```

## 🔧 Environment Variables (Optional)

| Variable | Purpose | Example |
|----------|---------|---------|
| `MONGO_ATLAS_USER` | Atlas username | `your_username` |
| `MONGO_ATLAS_PASS` | Atlas password | `your_password` |
| `MONGO_ATLAS_CLUSTER` | Atlas cluster name | `your_cluster_name` |
| `MONGO_URI` | Custom connection string | `mongodb://localhost:27017` |

## 👥 Multi-User Support

Each user has their own isolated credentials:

```bash
# Save credential for yourself (uses your OS username)
myapp add-cred api_key

# Save credential for another user
myapp add-cred api_key --user alice

# Retrieve credential for specific user
myapp get-cred api_key --user alice

# Delete credential (with confirmation)
myapp delete-cred api_key

# Delete credential for specific user
myapp delete-cred api_key --user alice

# Delete credential without confirmation
myapp delete-cred api_key --force

# Device management examples
myapp add-device aa:bb:cc:dd:ee:ff 192.168.1.100 my-laptop
myapp list-devices
# Copy the device ID from the list, then:
myapp remove-device 68fa964ad91cdaa009898a9c
# Or remove without confirmation:
myapp remove-device 68fa964ad91cdaa009898a9c --force
```

## 🛠️ Troubleshooting

### "Could not connect to MongoDB"
- **Check environment variables:** `echo $MONGO_ATLAS_USER`
- **Try local MongoDB:** Install with `brew install mongodb-community`
- **Check internet connection** (for Atlas)

### "command not found: myapp"
```bash
# Add Python bin to PATH
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc for permanent fix
```

### "No master key found"
```bash
myapp init
```

## 📱 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `myapp init` | Initialize master key | `myapp init` |
| `myapp add-cred <name>` | Add credential | `myapp add-cred github_token` |
| `myapp get-cred <name>` | Get credential | `myapp get-cred github_token` |
| `myapp delete-cred <name>` | Delete credential | `myapp delete-cred github_token` |
| `myapp add-device <mac> <ip> [hostname]` | Add device | `myapp add-device aa:bb:cc:dd:ee:ff 192.168.1.100 laptop` |
| `myapp list-devices` | List devices | `myapp list-devices` |
| `myapp remove-device <id>` | Remove device | `myapp remove-device 68fa964ad91cdaa009898a9c` |

## 🔒 Security Notes

- **Credentials are encrypted** before storage
- **Master key stored** in your OS keyring
- **Per-user isolation** - users can't see each other's credentials
- **Cloud storage** - accessible from anywhere with same environment variables

## 🌐 Cloud Database Benefits

- ✅ **Access from anywhere** - same data on all your devices
- ✅ **Automatic backups** - never lose your data
- ✅ **No local setup** - works immediately
- ✅ **Scalable** - handles multiple users and devices
- ✅ **Secure** - encrypted in transit and at rest

## 📞 Support

If you need help:
1. Check this guide first
2. Try the troubleshooting section
3. Verify your environment variables
4. Test with `myapp --help`
