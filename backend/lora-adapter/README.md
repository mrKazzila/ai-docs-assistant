# Создаем модель с адаптером


### 0. Скачать готовый адаптер
```shell
https://drive.google.com/file/d/1uQTknhcnQwPxug1H7A6T-FdhabwcNpuL/view
```

### 1. Скачайте базовую модель
```shell
ollama pull mistral:7b-instruct-v0.3-q4_K_M
```


### 2. Проверьте, что она скачалась
```shell
ollama list
```

### 3. Создайте Modelfile
```shell
cat > Modelfile << EOF
FROM mistral:7b-instruct-v0.3-q4_K_M
ADAPTER ./lora_adapter.gguf
EOF
```

### 4. Создайте модель с адаптером
```shell
ollama create my_api_docs -f Modelfile
```

### 5. Запустите
```shell
ollama run my_api_docs
```


### 6.Пример использования
```shell
ollama run my_api_docs "Привет, расскажи о API документации"
```

# Удалить модель (если понадобится)
```shell
ollama rm my_api_docs
```
