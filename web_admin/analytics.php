<?php
require_once 'config.php';
requireLogin();

// Initialize database connection
try {
    $pdo = new PDO('sqlite:' . DB_PATH);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die('Database connection failed: ' . $e->getMessage());
}

// Get analytics data
function getAnalytics($pdo) {
    $analytics = [];
    
    // Messages by day (last 30 days)
    $stmt = $pdo->query("
        SELECT DATE(timestamp) as date, COUNT(*) as count 
        FROM messages 
        WHERE datetime(timestamp) > datetime('now', '-30 days')
        GROUP BY DATE(timestamp) 
        ORDER BY date DESC
    ");
    $analytics['messages_by_day'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    // Top users by message count
    $stmt = $pdo->query("
        SELECT username, COUNT(*) as message_count 
        FROM messages 
        GROUP BY user_id, username 
        ORDER BY message_count DESC 
        LIMIT 10
    ");
    $analytics['top_users'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    // Model usage statistics
    $stmt = $pdo->query("
        SELECT model_used, COUNT(*) as usage_count, AVG(processing_time_ms) as avg_time
        FROM responses 
        WHERE model_used IS NOT NULL 
        GROUP BY model_used 
        ORDER BY usage_count DESC
    ");
    $analytics['model_usage'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    // Processing time statistics
    $stmt = $pdo->query("
        SELECT 
            AVG(processing_time_ms) as avg_time,
            MIN(processing_time_ms) as min_time,
            MAX(processing_time_ms) as max_time,
            COUNT(*) as total_responses
        FROM responses 
        WHERE processing_time_ms IS NOT NULL
    ");
    $analytics['processing_stats'] = $stmt->fetch(PDO::FETCH_ASSOC);
    
    // Channel activity
    $stmt = $pdo->query("
        SELECT 
            COALESCE(channel_name, 'Direct Message') as channel,
            COUNT(*) as message_count 
        FROM messages 
        GROUP BY channel_id, channel_name 
        ORDER BY message_count DESC 
        LIMIT 10
    ");
    $analytics['channel_activity'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    return $analytics;
}

$analytics = getAnalytics($pdo);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics - Database Admin</title>
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
        
        .nav-links {
            display: flex;
            gap: 1rem;
        }
        
        .nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            background: rgba(255,255,255,0.2);
            transition: background 0.3s;
        }
        
        .nav-links a:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .analytics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
        }
        
        .analytics-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .analytics-card h3 {
            margin-bottom: 1rem;
            color: #333;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .chart-container {
            height: 300px;
            display: flex;
            align-items: end;
            gap: 0.5rem;
            padding: 1rem 0;
            border-bottom: 2px solid #e1e5e9;
            position: relative;
        }
        
        .bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 3px 3px 0 0;
            min-width: 20px;
            position: relative;
            transition: all 0.3s;
        }
        
        .bar:hover {
            opacity: 0.8;
        }
        
        .bar-label {
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.7rem;
            color: #666;
            white-space: nowrap;
        }
        
        .bar-value {
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.7rem;
            color: #333;
            font-weight: 600;
        }
        
        .list-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .list-item:last-child {
            border-bottom: none;
        }
        
        .list-item .name {
            font-weight: 500;
            color: #333;
        }
        
        .list-item .value {
            color: #667eea;
            font-weight: 600;
        }
        
        .stats-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-box {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-box .icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .stat-box .number {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.25rem;
        }
        
        .stat-box .label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .no-data {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 2rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Analytics</h1>
        <div class="nav-links">
            <a href="index.php">🏠 Dashboard</a>
            <a href="messages.php">💬 Messages</a>
            <a href="responses.php">🤖 Responses</a>
            <a href="users.php">👥 Users</a>
            <a href="?logout=1">🚪 Logout</a>
        </div>
    </div>
    
    <div class="container">
        <?php if ($analytics['processing_stats']['total_responses'] > 0): ?>
            <div class="stats-summary">
                <div class="stat-box">
                    <div class="icon">⚡</div>
                    <div class="number"><?php echo number_format($analytics['processing_stats']['avg_time']); ?>ms</div>
                    <div class="label">Avg Processing Time</div>
                </div>
                <div class="stat-box">
                    <div class="icon">🚀</div>
                    <div class="number"><?php echo number_format($analytics['processing_stats']['min_time']); ?>ms</div>
                    <div class="label">Fastest Response</div>
                </div>
                <div class="stat-box">
                    <div class="icon">🐌</div>
                    <div class="number"><?php echo number_format($analytics['processing_stats']['max_time']); ?>ms</div>
                    <div class="label">Slowest Response</div>
                </div>
                <div class="stat-box">
                    <div class="icon">📈</div>
                    <div class="number"><?php echo number_format($analytics['processing_stats']['total_responses']); ?></div>
                    <div class="label">Total Responses</div>
                </div>
            </div>
        <?php endif; ?>
        
        <div class="analytics-grid">
            <div class="analytics-card">
                <h3>📅 Messages by Day (Last 30 Days)</h3>
                <?php if (!empty($analytics['messages_by_day'])): ?>
                    <div class="chart-container">
                        <?php 
                        $max_count = max(array_column($analytics['messages_by_day'], 'count'));
                        foreach (array_reverse($analytics['messages_by_day']) as $day): 
                            $height = ($day['count'] / $max_count) * 250;
                        ?>
                            <div class="bar" style="height: <?php echo $height; ?>px;">
                                <div class="bar-value"><?php echo $day['count']; ?></div>
                                <div class="bar-label"><?php echo date('m/d', strtotime($day['date'])); ?></div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php else: ?>
                    <div class="no-data">No message data available</div>
                <?php endif; ?>
            </div>
            
            <div class="analytics-card">
                <h3>👑 Top Users by Messages</h3>
                <?php if (!empty($analytics['top_users'])): ?>
                    <?php foreach ($analytics['top_users'] as $user): ?>
                        <div class="list-item">
                            <span class="name"><?php echo htmlspecialchars($user['username']); ?></span>
                            <span class="value"><?php echo number_format($user['message_count']); ?> messages</span>
                        </div>
                    <?php endforeach; ?>
                <?php else: ?>
                    <div class="no-data">No user data available</div>
                <?php endif; ?>
            </div>
            
            <div class="analytics-card">
                <h3>🤖 Model Usage Statistics</h3>
                <?php if (!empty($analytics['model_usage'])): ?>
                    <?php foreach ($analytics['model_usage'] as $model): ?>
                        <div class="list-item">
                            <div>
                                <div class="name"><?php echo htmlspecialchars($model['model_used']); ?></div>
                                <div style="font-size: 0.8rem; color: #666;">
                                    Avg: <?php echo number_format($model['avg_time']); ?>ms
                                </div>
                            </div>
                            <span class="value"><?php echo number_format($model['usage_count']); ?> uses</span>
                        </div>
                    <?php endforeach; ?>
                <?php else: ?>
                    <div class="no-data">No model usage data available</div>
                <?php endif; ?>
            </div>
            
            <div class="analytics-card">
                <h3>💬 Channel Activity</h3>
                <?php if (!empty($analytics['channel_activity'])): ?>
                    <?php foreach ($analytics['channel_activity'] as $channel): ?>
                        <div class="list-item">
                            <span class="name"><?php echo htmlspecialchars($channel['channel']); ?></span>
                            <span class="value"><?php echo number_format($channel['message_count']); ?> messages</span>
                        </div>
                    <?php endforeach; ?>
                <?php else: ?>
                    <div class="no-data">No channel data available</div>
                <?php endif; ?>
            </div>
        </div>
    </div>
</body>
</html>
