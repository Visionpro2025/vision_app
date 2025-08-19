# 🔢 Capa Gematría – Sistema Visión

La **Capa Gematría** traduce noticias relevantes al hebreo y calcula valores numéricos a partir de sus palabras clave.  
Es una de las capas centrales del sistema **Visión**, encargada de descubrir equivalencias ocultas y proyectarlas hacia la **Tabla T70**.

---

## 1. Rol principal
- Tomar frases clave de noticias relevantes (ya filtradas en **Capa Noticias**).  
- Traducirlas o transliterarlas al hebreo.  
- Calcular sus valores gemátricos.  
- Reducirlos de forma flexible para extraer patrones numéricos significativos.  
- Entregar resultados listos para reforzarse con **T70**.  

---

## 2. Entradas
- Archivo oficial de noticias filtradas: `__RUNS/NEWS/news_filtered_YYYYMMDD.csv`.  
- Corpus de Gematría (diccionarios y tablas):  
  1. `__CORPUS/GEMATRIA/lexicon_hebrew.yaml` – Diccionario maestro palabra → hebreo.  
  2. `__CORPUS/GEMATRIA/translit_table.csv` – Tabla de transliteración letra por letra.  
  3. `__CORPUS/GEMATRIA/stopwords_es.txt` – Stopwords español.  
  4. `__CORPUS/GEMATRIA/stopwords_en.txt` – Stopwords inglés.  
  5. `__CORPUS/GEMATRIA/patterns.yaml` – Radar semántico de frases clave.  
  6. `__CORPUS/GEMATRIA/bibliography.md` – Fuentes y referencias.  

---

## 3. Proceso interno
1. **Selección de frase clave**  
   - Usa `patterns.yaml` para identificar palabras detonantes.  
   - Elimina stopwords en español e inglés.  

2. **Traducción / transliteración al hebreo**  
   - Se consulta primero `lexicon_hebrew.yaml`.  
   - Si no está la palabra, se usa `translit_table.csv`.  

3. **Cálculo gemátrico**  
   - Valor total por suma de letras hebreas.  
   - Métodos de reducción:  
     - **Mispar Gadol** (valores completos).  
     - **Mispar Katan** (reducción a un dígito).  
     - **Mispar Siduri** (posición ordinal).  

4. **Normalización y salida**  
   - Se generan columnas con valor total, valor reducido y frase clave.  

---

## 4. Salida de datos
**Archivo oficial de salida:**