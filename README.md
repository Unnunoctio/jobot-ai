# 🧠 Jobot AI – Automatización Inteligente para Detección y Filtrado de Ofertas Laborales

Jobot AI es una arquitectura serverless en AWS diseñada para buscar, filtrar, priorizar y enviar automáticamente ofertas laborales basadas en la experiencia del usuario y un puntaje generado mediante modelos de IA (OpenAI, Anthropic o DeepSeek).

El sistema ejecuta spiders, agrupa resultados, evalúa cada oferta con modelos LLM, detecta duplicados, y finalmente envía un correo con las mejores oportunidades del día.

---

## 🏛️ Arquitectura General
El sistema utiliza una arquitectura totalmente serverless:

- **AWS SAM** para IaC  
- **AWS Lambda (Python 3.14 / ARM64)**  
- **DynamoDB** para configuración y control de duplicados  
- **S3** para almacenar la experiencia del usuario  
- **Step Functions** para orquestación  
- **EventBridge** para programación de ejecuciones

---

## 🚀 Características Principales
### 🔍 Web Scraping Automatizado
- Spiders independientes para **Laborum**, **GetOnBoard** y **Trabajando**.
- Ejecución dinámica definida en la configuración almacenada en DynamoDB.

### 🧭 Orquestación con Step Functions
Pipeline completo:
1. **LoadConfig** → carga configuración desde DynamoDB.
2. **RunSpiders** → ejecuta spiders en paralelo.
3. **MergeOffers** → unifica y agrupa resultados.
4. **ScoreOffers** → genera puntajes con IA usando OpenAI / Anthropic / DeepSeek.
5. **SendEmail** → envía correo con las mejores ofertas del día.
6. **Fin de ejecución**

### 🧠 IA para filtrado inteligente
- Selección de provider: `OPENAI | ANTHROPIC | DEEPSEEK`.
- Puntaje basado en `UserExperience.txt` almacenado en S3.
- Mínimo de score configurable.

### 🗃️ Persistencia y deduplicación
- Tabla `SeenOffersTable` en DynamoDB con TTL para evitar re-procesar ofertas repetidas.
- Configuración de spiders manejada en `SpiderConfigTable`.

### 📬 Notificaciones por correo
- Integración con **Resend** para enviar emails con las nuevas ofertas priorizadas.

### ⏱️ Automatización programada
- Trigger vía **EventBridge** para ejecutar el pipeline 4 veces al día (8:00, 12:00, 16:00 y 20:00 CLT).

---

## ⚙️ Parámetros Configurables

| Parámetro | Descripción |
|----------|-------------|
| `ProxyEndpoint` | Endpoint de proxy para evitar bloqueos Cloudflare |
| `AiProvider` | OPENAI / ANTHROPIC / DEEPSEEK |
| `AiApiKey` | API Key del proveedor de IA |
| `AiModel` | Modelo LLM a utilizar |
| `S3BucketName` | Nombre del bucket para experiencia |
| `UserExperienceFile` | Nombre del archivo con la experiencia del usuario |
| `MinScore` | Puntaje mínimo para filtrar ofertas |
| `ResendApiKey` | API Key de Resend |
| `EmailSender` | Email remitente |

---

## 📋 Requerimientos Previos
- AWS CLI configurado  
- SAM CLI instalado  
- Cuenta AWS  
- API Key del proveedor de IA  
- API Key de Resend  

---

## 🚀 Despliegue con AWS SAM
```bash
sam build
sam deploy --guided
```

---

## 📁 Estructura del Repositorio
```
/
├── src/
│   ├── core/
│   │   ├── spiders/
│   │   ├── pipeline/
│   │   └── ...
├── template.yaml
├── README.md
├── requirements.txt
└── ...
```

---
## 🤝 Contribuciones
Las contribuciones son bienvenidas.  
Puedes abrir issues o enviar Pull Requests.

---

## 📜 Licencia
Este proyecto está bajo la licencia MIT.

