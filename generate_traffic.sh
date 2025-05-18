while true; do
  curl -s -o /dev/null http://localhost:8000/
  curl -s -o /dev/null http://localhost:8000/items/$((RANDOM % 10 + 1))
  curl -s -o /dev/null http://localhost:8000/items/99 # Will generate 404s
  curl -s -o /dev/null http://localhost:8000/heavy-task
  curl -s -o /dev/null http://localhost:8000/error-prone # Will generate 5xx errors
  curl -s -X POST -H "Content-Type: application/json" -d '{"name":"Test Product","value":'$((RANDOM % 100))'.'$((RANDOM % 99))'}' -o /dev/null http://localhost:8000/items/
  sleep 0.01 # Adjust sleep time for more or less traffic
done