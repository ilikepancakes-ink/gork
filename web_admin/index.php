<?php
require_once 'config.php';
requireLogin();

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: login.php');
    exit;
}

// Initialize database connection
try {
    $pdo = new PDO('sqlite:' . DB_PATH);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die('Database connection failed: ' . $e->getMessage());
}

// Get database statistics
function getStats($pdo) {
    $stats = [];
    
    // Total messages
    $stmt = $pdo->query("SELECT COUNT(*) as count FROM messages");
    $stats['total_messages'] = $stmt->fetch()['count'];
    
    // Total responses
    $stmt = $pdo->query("SELECT COUNT(*) as count FROM responses");
    $stats['total_responses'] = $stmt->fetch()['count'];
    
    // Unique users
    $stmt = $pdo->query("SELECT COUNT(DISTINCT user_id) as count FROM messages");
    $stats['unique_users'] = $stmt->fetch()['count'];
    
    // Recent activity (last 24 hours)
    $stmt = $pdo->query("SELECT COUNT(*) as count FROM messages WHERE datetime(timestamp) > datetime('now', '-1 day')");
    $stats['recent_messages'] = $stmt->fetch()['count'];
    
    return $stats;
}

$stats = getStats($pdo);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Admin Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 1.5rem;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            text-decoration: none;
            transition: background 0.3s;
        }
        
        .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-card .icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .stat-card .number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .stat-card .label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        
        .nav-card {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
            text-decoration: none;
            color: inherit;
        }
        
        .nav-card:hover {
            transform: translateY(-5px);
        }
        
        .nav-card .icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .nav-card h3 {
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .nav-card p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .db-info {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-top: 2rem;
        }
        
        .db-info h3 {
            margin-bottom: 1rem;
            color: #333;
        }
        
        .db-info p {
            color: #666;
            margin-bottom: 0.5rem;
        }
        
        .db-info code {
            background: #f8f9fa;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗄️ Database Admin Dashboard</h1>
        <div class="user-info">
            <span>👤 <?php echo htmlspecialchars($_SESSION['username']); ?></span>
            <a href="?logout=1" class="logout-btn">🚪 Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">💬</div>
                <div class="number"><?php echo number_format($stats['total_messages']); ?></div>
                <div class="label">Total Messages</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🤖</div>
                <div class="number"><?php echo number_format($stats['total_responses']); ?></div>
                <div class="label">Bot Responses</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">👥</div>
                <div class="number"><?php echo number_format($stats['unique_users']); ?></div>
                <div class="label">Unique Users</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">⚡</div>
                <div class="number"><?php echo number_format($stats['recent_messages']); ?></div>
                <div class="label">Recent Messages (24h)</div>
            </div>
        </div>
        
        <div class="nav-grid">
            <a href="messages.php" class="nav-card">
                <div class="icon">💬</div>
                <h3>View Messages</h3>
                <p>Browse and search through all user messages with filtering options</p>
            </a>
            
            <a href="responses.php" class="nav-card">
                <div class="icon">🤖</div>
                <h3>Bot Responses</h3>
                <p>View bot responses, processing times, and model usage statistics</p>
            </a>
            
            <a href="users.php" class="nav-card">
                <div class="icon">👥</div>
                <h3>User Management</h3>
                <p>View user statistics, message history, and user activity patterns</p>
            </a>
            
            <a href="analytics.php" class="nav-card">
                <div class="icon">📊</div>
                <h3>Analytics</h3>
                <p>Detailed analytics, charts, and insights about bot usage</p>
            </a>
        </div>
        
        <div class="db-info">
            <h3>📁 Database Information</h3>
            <p><strong>Database Path:</strong> <code><?php echo htmlspecialchars(DB_PATH); ?></code></p>
            <p><strong>Database Size:</strong> <code><?php echo file_exists(DB_PATH) ? number_format(filesize(DB_PATH)) . ' bytes' : 'File not found'; ?></code></p>
            <p><strong>Last Modified:</strong> <code><?php echo file_exists(DB_PATH) ? date('Y-m-d H:i:s', filemtime(DB_PATH)) : 'N/A'; ?></code></p>
        </div>
    </div>
</body>
</html>
