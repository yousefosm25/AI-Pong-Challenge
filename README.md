# AI Pong Challenge 🧠🏓

A classic Pong game where the paddles are controlled by AI agents trained using the NEAT (NeuroEvolution of Augmenting Topologies) algorithm. This project demonstrates how artificial neural networks can evolve over generations to master a simple game like Pong — no hardcoded logic, just evolution.

## 🎮 Demo

[![Watch the video](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://youtu.be/YOUR_VIDEO_ID)

## 🧠 Powered By

- **AI Algorithm**: NEAT (via neat-python)
- Neural networks evolve using fitness scoring and genetic operations such as mutation and crossover.

## 💻 Project Type

> **Desktop Application**

## 🚀 Technologies Used

- Python 3.8+
- neat-python
- Pygame
- NumPy

## 📁 Project Structure

```
AI Pong Challenge/
├── pong/
│   ├── src/           # Source code
│   ├── config.txt     # NEAT configuration
│   ├── run.py         # Main entry point
│   └── requirements.txt
├── requirements.txt   # Project dependencies
└── README.md
```

## 📥 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yousefosm25/AI-Pong-Challenge
cd AI-Pong-Challenge
```

### 2. Create and activate a virtual environment (recommended)
```bash
python -m venv enve
source enve/bin/activate  # On Windows: enve\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the game
```bash
cd pong
python run.py
```

## 🎯 Features

- Self-learning AI via NEAT algorithm
- Real-time visualization of AI training
- Fitness-based evolution over generations
- Dynamic difficulty adjustment
- Configurable NEAT parameters via config.txt

## 🎮 How to Play

1. The game starts automatically with AI-controlled paddles
2. Watch as the AI learns and improves over generations
3. The fitness score increases as the AI gets better at playing
4. Training progress is saved automatically

## 📊 Training Progress

The AI's learning progress can be monitored through:
- Real-time gameplay visualization
- Fitness score tracking
- Generation statistics

## 📎 Links

- GitHub: https://github.com/yousefosm25/AI-Pong-Challenge
- YouTube Demo: https://youtu.be/YOUR_VIDEO_ID

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

MIT License. See `LICENSE` for more information.
