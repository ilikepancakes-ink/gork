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

// Get user statistics with settings
$query = "SELECT
            m.user_id,
            m.username,
            m.user_display_name,
            COUNT(DISTINCT m.id) as message_count,
            COUNT(DISTINCT r.id) as response_count,
            MIN(m.timestamp) as first_message,
            MAX(m.timestamp) as last_message,
            AVG(r.processing_time_ms) as avg_processing_time,
            us.nsfw_mode,
            us.content_filter_level,
            us.updated_at as settings_updated
          FROM messages m
          LEFT JOIN responses r ON m.message_id = r.original_message_id
          LEFT JOIN user_settings us ON m.user_id = us.user_id
          GROUP BY m.user_id, m.username, m.user_display_name, us.nsfw_mode, us.content_filter_level, us.updated_at
          ORDER BY message_count DESC";

$stmt = $pdo->query($query);
$users = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Handle user data deletion
if (isset($_POST['delete_user_data'])) {
    $user_id = $_POST['user_id'];
    try {
        $pdo->beginTransaction();
        
        // Delete responses first
        $stmt = $pdo->prepare("DELETE FROM responses WHERE original_message_id IN (SELECT message_id FROM messages WHERE user_id = ?)");
        $stmt->execute([$user_id]);
        
        // Delete messages
        $stmt = $pdo->prepare("DELETE FROM messages WHERE user_id = ?");
        $stmt->execute([$user_id]);
        
        $pdo->commit();
        $success = "User data deleted successfully";
        
        // Refresh the page to update the list
        header("Location: users.php?success=" . urlencode($success));
        exit;
    } catch (PDOException $e) {
        $pdo->rollBack();
        $error = "Error deleting user data: " . $e->getMessage();
    }
}

if (isset($_GET['success'])) {
    $success = $_GET['success'];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Users - Database Admin</title>
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
        
        .users-table {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .table th, .table td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #e1e5e9;
        }
        
        .table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        .table tr:hover {
            background: #f8f9fa;
        }
        
        .user-info {
            font-size: 0.9rem;
        }
        
        .user-info .username {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 0.2rem;
        }
        
        .user-info .display-name {
            color: #666;
            font-size: 0.8rem;
        }
        
        .user-info .user-id {
            color: #999;
            font-family: monospace;
            font-size: 0.7rem;
        }
        
        .stats {
            text-align: center;
        }
        
        .stats .number {
            font-weight: 600;
            color: #333;
        }
        
        .stats .label {
            font-size: 0.8rem;
            color: #666;
        }
        
        .timestamp {
            font-size: 0.9rem;
            color: #666;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            transition: all 0.3s;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
            font-size: 0.8rem;
            padding: 0.3rem 0.6rem;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .btn-info {
            background: #17a2b8;
            color: white;
            font-size: 0.8rem;
            padding: 0.3rem 0.6rem;
            margin-right: 0.5rem;
        }
        
        .btn-info:hover {
            background: #138496;
        }
        
        .alert {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .summary {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            text-align: center;
        }

        .nsfw-indicator {
            font-weight: 600;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }

        .nsfw-enabled {
            background: #ffe6e6;
            color: #d63384;
            border: 1px solid #f8d7da;
        }

        .nsfw-disabled {
            background: #e6f7e6;
            color: #198754;
            border: 1px solid #c3e6cb;
        }

        .filter-indicator {
            font-weight: 500;
            padding: 0.1rem 0.3rem;
            border-radius: 3px;
            font-size: 0.75rem;
        }
        
        .summary h3 {
            margin-bottom: 1rem;
            color: #333;
        }
        
        .summary .total-users {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>👥 Users</h1>
        <div class="nav-links">
            <a href="index.php">🏠 Dashboard</a>
            <a href="messages.php">💬 Messages</a>
            <a href="responses.php">🤖 Responses</a>
            <a href="?logout=1">🚪 Logout</a>
        </div>
    </div>
    
    <div class="container">
        <?php if (isset($success)): ?>
            <div class="alert alert-success">✅ <?php echo htmlspecialchars($success); ?></div>
        <?php endif; ?>
        
        <?php if (isset($error)): ?>
            <div class="alert alert-danger">❌ <?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        
        <div class="summary">
            <h3>📊 User Summary</h3>
            <div class="total-users"><?php echo count($users); ?></div>
            <div>Total Active Users</div>
        </div>
        
        <div class="users-table">
            <table class="table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Messages</th>
                        <th>Responses</th>
                        <th>NSFW Mode</th>
                        <th>Content Filter</th>
                        <th>Avg Processing Time</th>
                        <th>First Message</th>
                        <th>Last Message</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($users as $user): ?>
                        <tr>
                            <td>
                                <div class="user-info">
                                    <div class="username"><?php echo htmlspecialchars($user['username']); ?></div>
                                    <?php if ($user['user_display_name'] && $user['user_display_name'] !== $user['username']): ?>
                                        <div class="display-name"><?php echo htmlspecialchars($user['user_display_name']); ?></div>
                                    <?php endif; ?>
                                    <div class="user-id"><?php echo htmlspecialchars(substr($user['user_id'], 0, 12)); ?>...</div>
                                </div>
                            </td>
                            <td>
                                <div class="stats">
                                    <div class="number"><?php echo number_format($user['message_count']); ?></div>
                                    <div class="label">messages</div>
                                </div>
                            </td>
                            <td>
                                <div class="stats">
                                    <div class="number"><?php echo number_format($user['response_count']); ?></div>
                                    <div class="label">responses</div>
                                </div>
                            </td>
                            <td>
                                <div class="stats">
                                    <?php if ($user['nsfw_mode'] === '1' || $user['nsfw_mode'] === 1): ?>
                                        <div class="number" style="color: #ff6b6b;">🔞 Enabled</div>
                                        <div class="label">NSFW</div>
                                    <?php elseif ($user['nsfw_mode'] === '0' || $user['nsfw_mode'] === 0): ?>
                                        <div class="number" style="color: #51cf66;">✅ Disabled</div>
                                        <div class="label">Safe</div>
                                    <?php else: ?>
                                        <span style="color: #999;">Not Set</span>
                                    <?php endif; ?>
                                </div>
                            </td>
                            <td>
                                <div class="stats">
                                    <?php
                                    $filter_level = $user['content_filter_level'] ?? 'strict';
                                    $filter_colors = [
                                        'strict' => '#51cf66',
                                        'moderate' => '#ffd43b',
                                        'minimal' => '#ff6b6b'
                                    ];
                                    $filter_icons = [
                                        'strict' => '🛡️',
                                        'moderate' => '⚖️',
                                        'minimal' => '🔓'
                                    ];
                                    ?>
                                    <div class="number" style="color: <?php echo $filter_colors[$filter_level] ?? '#999'; ?>">
                                        <?php echo $filter_icons[$filter_level] ?? '❓'; ?> <?php echo ucfirst($filter_level); ?>
                                    </div>
                                    <div class="label">filter</div>
                                </div>
                            </td>
                            <td>
                                <div class="stats">
                                    <?php if ($user['avg_processing_time']): ?>
                                        <div class="number"><?php echo number_format($user['avg_processing_time']); ?>ms</div>
                                        <div class="label">avg time</div>
                                    <?php else: ?>
                                        <span style="color: #999;">N/A</span>
                                    <?php endif; ?>
                                </div>
                            </td>
                            <td class="timestamp">
                                <?php echo date('Y-m-d H:i', strtotime($user['first_message'])); ?>
                            </td>
                            <td class="timestamp">
                                <?php echo date('Y-m-d H:i', strtotime($user['last_message'])); ?>
                            </td>
                            <td>
                                <a href="messages.php?user=<?php echo urlencode($user['user_id']); ?>" class="btn btn-info">
                                    👁️ View Messages
                                </a>
                                <form method="POST" style="display: inline;" 
                                      onsubmit="return confirm('Are you sure you want to delete ALL data for this user? This cannot be undone!')">
                                    <input type="hidden" name="user_id" value="<?php echo htmlspecialchars($user['user_id']); ?>">
                                    <button type="submit" name="delete_user_data" class="btn btn-danger">🗑️ Delete All Data</button>
                                </form>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
