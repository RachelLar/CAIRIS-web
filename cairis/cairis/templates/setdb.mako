<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>Set DB | CAIRIS</title>
</head>
<body>
    <form action="${action_url}" method="post" enctype="text/html">
        <p>
            <label for="host">Host:</label>
            <input type="text" id="host" name="host" value="127.0.0.1" />
        </p>
        <p>
            <label for="port">Port:</label>
            <input type="text" id="port" name="port" value="3306" />
        </p>
        <p>
            <label for="user">User:</label>
            <input type="text" id="user" name="user" value="cairis" />
        </p>
        <p>
            <label for="passwd">Host:</label>
            <input type="password" id="passwd" name="passwd" value="cairis123" />
        </p>
        <p>
            <label for="db">DB:</label>
            <input type="text" id="db" name="db" value="cairis" />
        </p>
        <p>
            <input type="submit" />
        </p>
    </form>
</body>
</html>