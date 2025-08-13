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

// Handle response deletion
if (isset($_POST['delete_response'])) {
    $response_id = $_POST['response_id'];
    try {
        $stmt = $pdo->prepare("DELETE FROM responses WHERE id = ?");
        $stmt->execute([$response_id]);
        $success = "Response deleted successfully";
    } catch (PDOException $e) {
        $error = "Error deleting response: " . $e->getMessage();
    }
}

// Pagination and filtering
$page = max(1, intval($_GET['page'] ?? 1));
$per_page = 20;
$offset = ($page - 1) * $per_page;

$search = $_GET['search'] ?? '';
$model_filter = $_GET['model'] ?? '';

// Build query
$where_conditions = [];
$params = [];

if ($search) {
    $where_conditions[] = "(r.response_content LIKE ? OR m.username LIKE ?)";
    $params[] = "%$search%";
    $params[] = "%$search%";
}

if ($model_filter) {
    $where_conditions[] = "r.model_used = ?";
    $params[] = $model_filter;
}

$where_clause = $where_conditions ? "WHERE " . implode(" AND ", $where_conditions) : "";

// Get total count
$count_query = "SELECT COUNT(*) as total FROM responses r 
                LEFT JOIN messages m ON r.original_message_id = m.message_id 
                $where_clause";
$stmt = $pdo->prepare($count_query);
$stmt->execute($params);
$total_responses = $stmt->fetch()['total'];
$total_pages = ceil($total_responses / $per_page);

// Get responses
$query = "SELECT r.*, m.username, m.user_display_name, m.message_content as original_message
          FROM responses r 
          LEFT JOIN messages m ON r.original_message_id = m.message_id 
          $where_clause 
          ORDER BY r.timestamp DESC 
          LIMIT $per_page OFFSET $offset";

$stmt = $pdo->prepare($query);
$stmt->execute($params);
$responses = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Get unique models for filter
$models_stmt = $pdo->query("SELECT DISTINCT model_used FROM responses WHERE model_used IS NOT NULL ORDER BY model_used");
$models = $models_stmt->fetchAll(PDO::FETCH_COLUMN);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bot Responses - Database Admin</title>
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
        
        .responses-table {
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
        
        .response-content {
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .original-message {
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 0.9rem;
            color: #666;
        }
        
        .user-info {
            font-size: 0.9rem;
        }
        
        .user-info .username {
            font-weight: 600;
            color: #667eea;
        }
        
        .timestamp {
            font-size: 0.9rem;
            color: #666;
        }
        
        .model-badge {
            background: #e9ecef;
            color: #495057;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-size: 0.8rem;
            font-family: monospace;
        }
        
        .processing-time {
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
        <h1>🤖 Bot Responses</h1>
        <div class="nav-links">
            <a href="index.php">🏠 Dashboard</a>
            <a href="messages.php">💬 Messages</a>
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
                    <label for="search">Search Responses</label>
                    <input type="text" id="search" name="search"
                           placeholder="Search in response content or username..."
                           value="<?php echo htmlspecialchars($search); ?>">
                </div>

                <div class="form-group">
                    <label for="model">Filter by Model</label>
                    <select id="model" name="model">
                        <option value="">All Models</option>
                        <?php foreach ($models as $model): ?>
                            <option value="<?php echo htmlspecialchars($model); ?>"
                                    <?php echo $model_filter === $model ? 'selected' : ''; ?>>
                                <?php echo htmlspecialchars($model); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <button type="submit" class="btn btn-primary">🔍 Filter</button>
            </form>
        </div>

        <div class="stats">
            Showing <?php echo number_format($total_responses); ?> responses
            (Page <?php echo $page; ?> of <?php echo $total_pages; ?>)
        </div>

        <div class="responses-table">
            <table class="table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Original Message</th>
                        <th>Bot Response</th>
                        <th>Model</th>
                        <th>Processing Time</th>
                        <th>Timestamp</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($responses as $response): ?>
                        <tr>
                            <td>
                                <div class="user-info">
                                    <div class="username"><?php echo htmlspecialchars($response['username'] ?? 'Unknown'); ?></div>
                                </div>
                            </td>
                            <td>
                                <div class="original-message" title="<?php echo htmlspecialchars($response['original_message'] ?? ''); ?>">
                                    <?php echo htmlspecialchars($response['original_message'] ?? 'N/A'); ?>
                                </div>
                            </td>
                            <td>
                                <div class="response-content" title="<?php echo htmlspecialchars($response['response_content']); ?>">
                                    <?php echo htmlspecialchars($response['response_content']); ?>
                                </div>
                            </td>
                            <td>
                                <?php if ($response['model_used']): ?>
                                    <span class="model-badge"><?php echo htmlspecialchars($response['model_used']); ?></span>
                                <?php else: ?>
                                    <span style="color: #999;">N/A</span>
                                <?php endif; ?>
                            </td>
                            <td class="processing-time">
                                <?php if ($response['processing_time_ms']): ?>
                                    <?php echo number_format($response['processing_time_ms']); ?>ms
                                <?php else: ?>
                                    <span style="color: #999;">N/A</span>
                                <?php endif; ?>
                            </td>
                            <td class="timestamp">
                                <?php echo date('Y-m-d H:i:s', strtotime($response['timestamp'])); ?>
                            </td>
                            <td>
                                <form method="POST" style="display: inline;"
                                      onsubmit="return confirm('Are you sure you want to delete this response?')">
                                    <input type="hidden" name="response_id" value="<?php echo htmlspecialchars($response['id']); ?>">
                                    <button type="submit" name="delete_response" class="btn btn-danger">🗑️ Delete</button>
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
                    <a href="?page=<?php echo $page - 1; ?>&search=<?php echo urlencode($search); ?>&model=<?php echo urlencode($model_filter); ?>">« Previous</a>
                <?php endif; ?>

                <?php for ($i = max(1, $page - 2); $i <= min($total_pages, $page + 2); $i++): ?>
                    <?php if ($i == $page): ?>
                        <span class="current"><?php echo $i; ?></span>
                    <?php else: ?>
                        <a href="?page=<?php echo $i; ?>&search=<?php echo urlencode($search); ?>&model=<?php echo urlencode($model_filter); ?>"><?php echo $i; ?></a>
                    <?php endif; ?>
                <?php endfor; ?>

                <?php if ($page < $total_pages): ?>
                    <a href="?page=<?php echo $page + 1; ?>&search=<?php echo urlencode($search); ?>&model=<?php echo urlencode($model_filter); ?>">Next »</a>
                <?php endif; ?>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
