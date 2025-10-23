#!/bin/bash
# Quick setup script for new users

echo "🚀 MyApp Quick Setup"
echo "===================="
echo ""

# Check if myapp is installed
if ! command -v myapp &> /dev/null; then
    echo "❌ MyApp not found. Please install it first:"
    echo "   pip install myapp-secure-cli"
    echo ""
    exit 1
fi

echo "✅ MyApp is installed"
echo ""

# Ask user for setup preference
echo "Choose your database setup:"
echo "1) Use our cloud database (easiest - no setup required)"
echo "2) Use your own MongoDB Atlas"
echo "3) Use local MongoDB"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🌐 Setting up cloud database connection..."
        export MONGO_ATLAS_USER="benananekhalilo_db_user"
        export MONGO_ATLAS_PASS="vUMZOj5VO5RwAxGL"
        export MONGO_ATLAS_CLUSTER="keypass.kq91w0b"
        
        # Add to shell profile for persistence
        echo "" >> ~/.bashrc
        echo "# MyApp cloud database settings" >> ~/.bashrc
        echo "export MONGO_ATLAS_USER=\"benananekhalilo_db_user\"" >> ~/.bashrc
        echo "export MONGO_ATLAS_PASS=\"vUMZOj5VO5RwAxGL\"" >> ~/.bashrc
        echo "export MONGO_ATLAS_CLUSTER=\"keypass.kq91w0b\"" >> ~/.bashrc
        
        echo "✅ Cloud database configured!"
        echo "   Your data will be stored in our secure cloud database"
        ;;
    2)
        echo ""
        echo "🌐 Setting up your own Atlas database..."
        read -p "Enter your Atlas username: " atlas_user
        read -p "Enter your Atlas password: " atlas_pass
        read -p "Enter your Atlas cluster name: " atlas_cluster
        
        export MONGO_ATLAS_USER="$atlas_user"
        export MONGO_ATLAS_PASS="$atlas_pass"
        export MONGO_ATLAS_CLUSTER="$atlas_cluster"
        
        # Add to shell profile for persistence
        echo "" >> ~/.bashrc
        echo "# MyApp Atlas settings" >> ~/.bashrc
        echo "export MONGO_ATLAS_USER=\"$atlas_user\"" >> ~/.bashrc
        echo "export MONGO_ATLAS_PASS=\"$atlas_pass\"" >> ~/.bashrc
        echo "export MONGO_ATLAS_CLUSTER=\"$atlas_cluster\"" >> ~/.bashrc
        
        echo "✅ Your Atlas database configured!"
        ;;
    3)
        echo ""
        echo "🏠 Setting up local MongoDB..."
        echo "Please install MongoDB locally:"
        echo "  macOS: brew install mongodb-community"
        echo "  Ubuntu: sudo apt install mongodb"
        echo "  Windows: Download from https://mongodb.com"
        echo ""
        echo "Then start MongoDB:"
        echo "  macOS: brew services start mongodb-community"
        echo "  Ubuntu: sudo systemctl start mongodb"
        echo ""
        echo "No environment variables needed for local setup."
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🔑 Initializing MyApp..."
myapp init

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Try these commands:"
echo "  myapp add-cred github_token"
echo "  myapp get-cred github_token"
echo "  myapp add-device aa:bb:cc:dd:ee:ff 192.168.1.100 my-laptop"
echo "  myapp list-devices"
echo ""
echo "📖 For more help, see USER_GUIDE.md"
