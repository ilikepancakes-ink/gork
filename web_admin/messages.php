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

// Handle message deletion
if (isset($_POST['delete_message'])) {
    $message_id = $_POST['message_id'];
    try {
        // Delete responses first (foreign key constraint)
        $stmt = $pdo->prepare("DELETE FROM responses WHERE original_message_id = ?");
        $stmt->execute([$message_id]);
        
        // Delete the message
        $stmt = $pdo->prepare("DELETE FROM messages WHERE message_id = ?");
        $stmt->execute([$message_id]);
        
        $success = "Message deleted successfully";
    } catch (PDOException $e) {
        $error = "Error deleting message: " . $e->getMessage();
    }
}

// Pagination and filtering
$page = max(1, intval($_GET['page'] ?? 1));
$per_page = 20;
$offset = ($page - 1) * $per_page;

$search = $_GET['search'] ?? '';
$user_filter = $_GET['user'] ?? '';

// Build query
$where_conditions = [];
$params = [];

if ($search) {
    $where_conditions[] = "(message_content LIKE ? OR username LIKE ?)";
    $params[] = "%$search%";
    $params[] = "%$search%";
}

if ($user_filter) {
    $where_conditions[] = "user_id = ?";
    $params[] = $user_filter;
}

$where_clause = $where_conditions ? "WHERE " . implode(" AND ", $where_conditions) : "";

// Get total count
$count_query = "SELECT COUNT(*) as total FROM messages $where_clause";
$stmt = $pdo->prepare($count_query);
$stmt->execute($params);
$total_messages = $stmt->fetch()['total'];
$total_pages = ceil($total_messages / $per_page);

// Get messages
$query = "SELECT m.*, 
                 (SELECT COUNT(*) FROM responses r WHERE r.original_message_id = m.message_id) as response_count
          FROM messages m 
          $where_clause 
          ORDER BY m.timestamp DESC 
          LIMIT $per_page OFFSET $offset";

$stmt = $pdo->prepare($query);
$stmt->execute($params);
$messages = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Get unique users for filter
$users_stmt = $pdo->query("SELECT DISTINCT user_id, username FROM messages ORDER BY username");
$users = $users_stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Messages - Database Admin</title>
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
        
        .filters {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .filters form {
            display: grid;
            grid-template-columns: 1fr 200px auto;
            gap: 1rem;
            align-items: end;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 0.5rem;
            border: 2px solid #e1e5e9;
            border-radius: 5px;
            font-size: 1rem;
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
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
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
        
        .messages-table {
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
        
        .message-content {
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .user-info {
            font-size: 0.9rem;
        }
        
        .user-info .username {
            font-weight: 600;
            color: #667eea;
        }
        
        .user-info .user-id {
            color: #666;
            font-family: monospace;
        }
        
        .timestamp {
            font-size: 0.9rem;
            color: #666;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 2rem;
        }
        
        .pagination a, .pagination span {
            padding: 0.5rem 1rem;
            border: 1px solid #e1e5e9;
            border-radius: 5px;
            text-decoration: none;
            color: #333;
        }
        
        .pagination a:hover {
            background: #f8f9fa;
        }
        
        .pagination .current {
            background: #667eea;
            color: white;
            border-color: #667eea;
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
        
        .stats {
            text-align: center;
            margin-bottom: 1rem;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>💬 Messages</h1>
        <div class="nav-links">
            <a href="index.php">🏠 Dashboard</a>
            <a href="responses.php">🤖 Responses</a>
            <a href="users.php">👥 Users</a>
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
        
        <div class="filters">
            <form method="GET">
                <div class="form-group">
                    <label for="search">Search Messages</label>
                    <input type="text" id="search" name="search" 
                           placeholder="Search in message content or username..."
                           value="<?php echo htmlspecialchars($search); ?>">
                </div>
                
                <div class="form-group">
                    <label for="user">Filter by User</label>
                    <select id="user" name="user">
                        <option value="">All Users</option>
                        <?php foreach ($users as $user): ?>
                            <option value="<?php echo htmlspecialchars($user['user_id']); ?>"
                                    <?php echo $user_filter === $user['user_id'] ? 'selected' : ''; ?>>
                                <?php echo htmlspecialchars($user['username']); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                
                <button type="submit" class="btn btn-primary">🔍 Filter</button>
            </form>
        </div>
        
        <div class="stats">
            Showing <?php echo number_format($total_messages); ?> messages 
            (Page <?php echo $page; ?> of <?php echo $total_pages; ?>)
        </div>
        
        <div class="messages-table">
            <table class="table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Message</th>
                        <th>Channel</th>
                        <th>Timestamp</th>
                        <th>Responses</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($messages as $message): ?>
                        <tr>
                            <td>
                                <div class="user-info">
                                    <div class="username"><?php echo htmlspecialchars($message['username']); ?></div>
                                    <div class="user-id"><?php echo htmlspecialchars(substr($message['user_id'], 0, 8)); ?>...</div>
                                </div>
                            </td>
                            <td>
                                <div class="message-content" title="<?php echo htmlspecialchars($message['message_content']); ?>">
                                    <?php echo htmlspecialchars($message['message_content']); ?>
                                </div>
                            </td>
                            <td>
                                <div><?php echo htmlspecialchars($message['channel_name'] ?? 'DM'); ?></div>
                                <div style="font-size: 0.8rem; color: #666;">
                                    <?php echo htmlspecialchars($message['guild_name'] ?? 'Direct Message'); ?>
                                </div>
                            </td>
                            <td class="timestamp">
                                <?php echo date('Y-m-d H:i:s', strtotime($message['timestamp'])); ?>
                            </td>
                            <td>
                                <?php echo $message['response_count']; ?> responses
                            </td>
                            <td>
                                <form method="POST" style="display: inline;" 
                                      onsubmit="return confirm('Are you sure you want to delete this message?')">
                                    <input type="hidden" name="message_id" value="<?php echo htmlspecialchars($message['message_id']); ?>">
                                    <button type="submit" name="delete_message" class="btn btn-danger">🗑️ Delete</button>
                                </form>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        
        <?php if ($total_pages > 1): ?>
            <div class="pagination">
                <?php if ($page > 1): ?>
                    <a href="?page=<?php echo $page - 1; ?>&search=<?php echo urlencode($search); ?>&user=<?php echo urlencode($user_filter); ?>">« Previous</a>
                <?php endif; ?>
                
                <?php for ($i = max(1, $page - 2); $i <= min($total_pages, $page + 2); $i++): ?>
                    <?php if ($i == $page): ?>
                        <span class="current"><?php echo $i; ?></span>
                    <?php else: ?>
                        <a href="?page=<?php echo $i; ?>&search=<?php echo urlencode($search); ?>&user=<?php echo urlencode($user_filter); ?>"><?php echo $i; ?></a>
                    <?php endif; ?>
                <?php endfor; ?>
                
                <?php if ($page < $total_pages): ?>
                    <a href="?page=<?php echo $page + 1; ?>&search=<?php echo urlencode($search); ?>&user=<?php echo urlencode($user_filter); ?>">Next »</a>
                <?php endif; ?>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
