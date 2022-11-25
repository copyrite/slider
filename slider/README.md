## Notes

For now, this file is just for storing SQL snippets.

#### Number of leaderboard entries of each player
```
sqlite3 slider.db "SELECT user.handle, count(*) FROM lb INNER JOIN user ON user.id = lb.user GROUP BY user.id ORDER BY 2 DESC"
```

#### List of #1 positions of each leaderboard
```
sqlite3 slider.db "SELECT user.handle, lb.track, lb.car, min(lb.time) FROM lb INNER JOIN user ON user.id = lb.user GROUP BY lb.track, lb.car HAVING time = min(lb.time) ORDER BY lb.time"
```

#### Number of #1 positions held of each player"
```
sqlite3 slider.db "SELECT user.handle, count(*) FROM (SELECT lb.user, lb.track, lb.car, min(lb.time) FROM lb GROUP BY lb.track, lb.car HAVING time = min(lb.time) ORDER BY lb.time) INNER JOIN user ON user.id = user GROUP BY user ORDER BY 2 DESC"
```

#### `WR time / PB time` points per leaderboard entry
```
sqlite3 slider.db "SELECT user.handle, sum(CAST(top.time AS float) / lb.time) FROM lb INNER JOIN user ON user.id = lb.user INNER JOIN (SELECT lb.track, lb.car, lb.time FROM lb GROUP BY lb.track, lb.car HAVING time = min(lb.time)) AS top ON top.track = lb.track AND top.car = lb.car GROUP BY user.id ORDER BY 2 DESC"
```

#### Same, but builtins only
sqlite3 slider.db "SELECT user.handle, sum(CAST(top.time AS float) / lb.time) FROM lb INNER JOIN user ON user.id = lb.user INNER JOIN (SELECT lb.track, lb.car, lb.time FROM lb GROUP BY lb.track, lb.car HAVING time = min(lb.time)) AS top ON top.track = lb.track AND top.car = lb.car INNER JOIN track ON lb.track = track.name WHERE track.is_builtin = true GROUP BY user.id ORDER BY 2 DESC"
