#!/bin/bash
# Network Configuration Helper for Ethics-Bench External Access

echo "🔍 ETHICS-BENCH NETWORK DIAGNOSTICS"
echo "================================================="

# Get local IP address
if command -v ipconfig >/dev/null 2>&1; then
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null)
    if [ -z "$LOCAL_IP" ]; then
        LOCAL_IP=$(ipconfig getifaddr en1 2>/dev/null)
    fi
elif command -v hostname >/dev/null 2>&1; then
    LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null)
fi

if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="Unable to detect"
fi

PUBLIC_IP="76.103.207.23"

echo "📍 Network Information:"
echo "   Local IP Address: $LOCAL_IP"
echo "   Public IP Address: $PUBLIC_IP"
echo ""

# Check if ports are listening locally
echo "🔌 Local Port Status:"
for port in 9002 9012; do
    if netstat -an 2>/dev/null | grep -q ":$port.*LISTEN"; then
        echo "   ✅ Port $port is listening locally"
    else
        echo "   ❌ Port $port is NOT listening locally"
    fi
done
echo ""

# Test local connectivity
echo "🏠 Local Connectivity Test:"
for port in 9002 9012; do
    if curl -s --connect-timeout 2 http://localhost:$port/.well-known/agent-card.json >/dev/null 2>&1; then
        echo "   ✅ localhost:$port responds"
    else
        echo "   ❌ localhost:$port does not respond"
    fi
done
echo ""

# Test external connectivity
echo "🌐 External Connectivity Test:"
for port in 9002 9012; do
    echo "   Testing $PUBLIC_IP:$port..."
    if curl -s --connect-timeout 5 http://$PUBLIC_IP:$port/.well-known/agent-card.json >/dev/null 2>&1; then
        echo "   ✅ $PUBLIC_IP:$port is accessible externally"
    else
        echo "   ❌ $PUBLIC_IP:$port is NOT accessible externally"
    fi
done
echo ""

echo "🛠️  ROUTER CONFIGURATION NEEDED"
echo "================================================="
echo "To make your agents accessible externally, configure port forwarding:"
echo ""
echo "1. 📶 Access your router's admin panel:"
echo "   - Open browser and go to: http://192.168.1.1 or http://192.168.0.1"
echo "   - Login with admin credentials"
echo ""
echo "2. 🔧 Find Port Forwarding settings:"
echo "   - Look for 'Port Forwarding', 'Virtual Server', or 'NAT' settings"
echo ""
echo "3. ➕ Add these forwarding rules:"
echo "   Rule 1:"
echo "     - External Port: 9002"
echo "     - Internal IP: $LOCAL_IP"
echo "     - Internal Port: 9002"
echo "     - Protocol: TCP"
echo ""
echo "   Rule 2:"
echo "     - External Port: 9012"
echo "     - Internal IP: $LOCAL_IP" 
echo "     - Internal Port: 9012"
echo "     - Protocol: TCP"
echo ""
echo "4. 💾 Save settings and restart router"
echo ""
echo "5. 🔒 Check firewall settings:"
echo "   - Ensure macOS firewall allows incoming connections on ports 9002, 9012"
echo "   - System Preferences > Security & Privacy > Firewall > Firewall Options"
echo ""

echo "🚀 ALTERNATIVE: Use ngrok for testing"
echo "================================================="
echo "For quick testing without router config:"
echo ""
echo "1. Install ngrok: brew install ngrok"
echo "2. Start tunnels:"
echo "   ngrok http 9002 --region us &"
echo "   ngrok http 9012 --region us &"
echo "3. Use the provided https URLs for external access"
echo ""

echo "🎯 AGENTBEATS REGISTRATION URLs"
echo "================================================="
echo "Once external access works, register with:"
echo ""
echo "Green Agent:"
echo "   Agent URL: http://$PUBLIC_IP:9012"
echo "   Launcher URL: http://$PUBLIC_IP:9010"
echo ""
echo "White Agent:"
echo "   Agent URL: http://$PUBLIC_IP:9002"
echo "   Launcher URL: http://$PUBLIC_IP:9000"