# FlowCharTron!
Это проект, который автоматически генерирует блок-схемы в формате draw.io по стандарту ГОСТ 19.701-90. По крайней мере пытается.

## Как это счастье поставить?
Скачайте файл из релизов и пропишите:
### Linux/Mac OS:
```bash
python3 -m pip install flowchartron-0.1a1-py3-none-any.whl
```

### Windows:
```bash
python -m pip install flowchartron-0.1a1-py3-none-any.whl
```

## Как этим пользоваться?
Чтобы запустить эту программу откройте командную строку или терминал и пропишите
```bash
flowchartron
```

Вставьте свою функцию или метод в программу, сгенерируйте XML, а затем сделайте эспорт в изображение. 
Не забудьте помолиться три раза, иначе боги OpenAI не дадут вам блок-схемы, увы.

## Какого вида генерируется XML через ChatGPT?
Вот формат блок-схемы и как каждый блок должен использоваться:
```xml
<flowchart>
    <BasicBlock label="operation"/>
    <WhileBlock label="while">
        <BasicBlock label="label"/>
        <BasicBlock label="label"/>
    <WhileBlock/>
    <ForBlock label="while">
        <BasicBlock label="label"/>
        <BasicBlock label="label"/>
    <ForBlock/>
    <DecisionBlock label="condition">
        <condition label="label">
            <BasicBlock label="label"/>
        </condition>
    </DecisionBlock>
</flowchart>

```
