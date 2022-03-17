Fotolei PssA 系统

### customization for mysql-connector

add below method for mysql/connector/pooling.py/PooledMySQLConnection

```python
    @property
    def cnx(self):
        """Return the real connection"""
        return self._cnx
```
