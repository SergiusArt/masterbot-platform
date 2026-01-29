#!/bin/bash
# Script to automate SSH key setup for passwordless login

set -e

echo "🔐 SSH Passwordless Login Setup"
echo "================================"
echo ""

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "📝 SSH key not found. Creating new SSH key..."
    read -p "Enter your email: " email
    ssh-keygen -t rsa -b 4096 -C "$email" -f ~/.ssh/id_rsa -N ""
    echo "✅ SSH key created!"
else
    echo "✅ SSH key already exists at ~/.ssh/id_rsa"
fi

echo ""
echo "📋 Your public key:"
cat ~/.ssh/id_rsa.pub
echo ""

# Get server details
read -p "Enter server IP address: " server_ip
read -p "Enter username on server: " username
read -p "Enter SSH port (default 22): " port
port=${port:-22}

# Optional: SSH config alias
read -p "Enter alias name for this server (e.g., 'myserver'): " alias_name

echo ""
echo "🔄 Copying SSH key to server..."
ssh-copy-id -p $port $username@$server_ip

if [ $? -eq 0 ]; then
    echo "✅ SSH key successfully copied to server!"

    # Create SSH config entry
    if [ ! -z "$alias_name" ]; then
        echo ""
        echo "📝 Creating SSH config entry..."

        mkdir -p ~/.ssh
        touch ~/.ssh/config
        chmod 600 ~/.ssh/config

        # Check if entry already exists
        if grep -q "Host $alias_name" ~/.ssh/config; then
            echo "⚠️  Entry for '$alias_name' already exists in ~/.ssh/config"
        else
            cat >> ~/.ssh/config << EOF

Host $alias_name
    HostName $server_ip
    User $username
    Port $port
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
            echo "✅ SSH config entry created!"
            echo ""
            echo "You can now connect with: ssh $alias_name"
        fi
    fi

    echo ""
    echo "🧪 Testing connection..."
    ssh -p $port $username@$server_ip "echo '✅ Connection successful!'"

    echo ""
    echo "================================================"
    echo "✅ Setup complete!"
    echo ""
    echo "You can now connect without password:"
    if [ ! -z "$alias_name" ]; then
        echo "  ssh $alias_name"
    else
        echo "  ssh -p $port $username@$server_ip"
    fi
    echo ""
    echo "📌 Recommended: Disable password authentication on server"
    echo "   Run on server:"
    echo "   sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config"
    echo "   sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config"
    echo "   sudo systemctl restart sshd"
    echo "================================================"
else
    echo "❌ Failed to copy SSH key. Please check:"
    echo "   - Server IP address is correct"
    echo "   - Username is correct"
    echo "   - You can login with password"
    echo "   - Firewall allows SSH connections"
    exit 1
fi
