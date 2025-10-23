// Game Controller - Manages game state, rendering, and interaction

class GameController {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');

        this.game = new MazeGame({height: 12, width: 12}, 5);
        this.agent = new QLearningAgent();

        // Try to load saved agent
        this.agent.load();

        this.mode = 'manual'; // 'manual' or 'ai'
        this.isPlaying = false;
        this.isTraining = false;
        this.trainingIntervalId = null;

        this.cellSize = Math.min(
            this.canvas.width / this.game.width,
            this.canvas.height / this.game.height
        );

        // Setup keyboard controls
        this.setupKeyboardControls();

        // Initial render
        this.render();
        this.updateUI();
    }

    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            if (this.mode !== 'manual' || this.game.caught || this.game.won) {
                return;
            }

            let action = null;
            switch (e.key) {
                case 'ArrowUp':
                    action = MazeGame.UP;
                    e.preventDefault();
                    break;
                case 'ArrowDown':
                    action = MazeGame.DOWN;
                    e.preventDefault();
                    break;
                case 'ArrowLeft':
                    action = MazeGame.LEFT;
                    e.preventDefault();
                    break;
                case 'ArrowRight':
                    action = MazeGame.RIGHT;
                    e.preventDefault();
                    break;
            }

            if (action !== null) {
                this.game.step(action);
                this.render();
                this.updateUI();
                this.checkGameOver();
            }
        });
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw maze
        for (let i = 0; i < this.game.height; i++) {
            for (let j = 0; j < this.game.width; j++) {
                const x = j * this.cellSize;
                const y = i * this.cellSize;

                // Draw cell background
                if (this.game.maze[i][j] === MazeGame.WALL) {
                    this.ctx.fillStyle = '#1f2937';
                    this.ctx.fillRect(x, y, this.cellSize, this.cellSize);
                } else {
                    this.ctx.fillStyle = '#ffffff';
                    this.ctx.fillRect(x, y, this.cellSize, this.cellSize);

                    // Draw grid lines
                    this.ctx.strokeStyle = '#e5e7eb';
                    this.ctx.strokeRect(x, y, this.cellSize, this.cellSize);
                }

                // Draw exit
                if (i === this.game.exitPos.row && j === this.game.exitPos.col) {
                    this.ctx.fillStyle = '#10b981';
                    this.ctx.fillRect(
                        x + this.cellSize * 0.1,
                        y + this.cellSize * 0.1,
                        this.cellSize * 0.8,
                        this.cellSize * 0.8
                    );

                    // Draw "E" for exit
                    this.ctx.fillStyle = '#ffffff';
                    this.ctx.font = `bold ${this.cellSize * 0.5}px Arial`;
                    this.ctx.textAlign = 'center';
                    this.ctx.textBaseline = 'middle';
                    this.ctx.fillText('E', x + this.cellSize / 2, y + this.cellSize / 2);
                }
            }
        }

        // Draw coins
        this.ctx.fillStyle = '#fbbf24';
        for (const coin of this.game.coins) {
            const x = coin.col * this.cellSize + this.cellSize / 2;
            const y = coin.row * this.cellSize + this.cellSize / 2;
            const radius = this.cellSize * 0.25;

            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, Math.PI * 2);
            this.ctx.fill();

            // Coin outline
            this.ctx.strokeStyle = '#f59e0b';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();

            // Coin symbol
            this.ctx.fillStyle = '#78350f';
            this.ctx.font = `bold ${this.cellSize * 0.3}px Arial`;
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText('$', x, y);
        }

        // Draw NPC
        const npcX = this.game.npcPos.col * this.cellSize + this.cellSize / 2;
        const npcY = this.game.npcPos.row * this.cellSize + this.cellSize / 2;
        const npcRadius = this.cellSize * 0.35;

        this.ctx.fillStyle = '#ef4444';
        this.ctx.beginPath();
        this.ctx.arc(npcX, npcY, npcRadius, 0, Math.PI * 2);
        this.ctx.fill();

        // NPC eyes
        this.ctx.fillStyle = '#ffffff';
        const eyeOffset = this.cellSize * 0.12;
        const eyeRadius = this.cellSize * 0.08;
        this.ctx.beginPath();
        this.ctx.arc(npcX - eyeOffset, npcY - eyeOffset, eyeRadius, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.arc(npcX + eyeOffset, npcY - eyeOffset, eyeRadius, 0, Math.PI * 2);
        this.ctx.fill();

        // Draw Player
        const playerX = this.game.playerPos.col * this.cellSize + this.cellSize / 2;
        const playerY = this.game.playerPos.row * this.cellSize + this.cellSize / 2;
        const playerRadius = this.cellSize * 0.35;

        this.ctx.fillStyle = '#3b82f6';
        this.ctx.beginPath();
        this.ctx.arc(playerX, playerY, playerRadius, 0, Math.PI * 2);
        this.ctx.fill();

        // Player marker
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(playerX, playerY, playerRadius * 0.5, 0, Math.PI * 2);
        this.ctx.fill();
    }

    updateUI() {
        document.getElementById('score').textContent = this.game.score;
        document.getElementById('steps').textContent = `${this.game.steps}/${this.game.maxSteps}`;
        document.getElementById('coins').textContent = this.game.coins.length;
        document.getElementById('mode').textContent = this.mode === 'manual' ? 'Manual' : 'AI Playing';
    }

    checkGameOver() {
        const statusMessage = document.getElementById('statusMessage');

        if (this.game.won) {
            statusMessage.textContent = '🎉 YOU WON! 🎉';
            statusMessage.className = 'status-message won';
            if (this.mode === 'ai') {
                this.stopAI();
            }
        } else if (this.game.caught) {
            statusMessage.textContent = '💀 CAUGHT BY NPC! 💀';
            statusMessage.className = 'status-message lost';
            if (this.mode === 'ai') {
                this.stopAI();
            }
        } else if (this.game.steps >= this.game.maxSteps) {
            statusMessage.textContent = '⏱️ TIME OUT! ⏱️';
            statusMessage.className = 'status-message lost';
            if (this.mode === 'ai') {
                this.stopAI();
            }
        } else {
            statusMessage.style.display = 'none';
        }
    }

    startAI() {
        if (this.isPlaying) return;

        this.isPlaying = true;
        const playStep = () => {
            if (!this.isPlaying || this.game.caught || this.game.won ||
                this.game.steps >= this.game.maxSteps) {
                this.isPlaying = false;
                this.checkGameOver();
                return;
            }

            const state = this.game.getStateRepresentation();
            const action = this.agent.getAction(state, false); // No exploration
            this.game.step(action);
            this.render();
            this.updateUI();

            setTimeout(playStep, 150); // Delay between moves
        };

        playStep();
    }

    stopAI() {
        this.isPlaying = false;
    }

    async startTraining() {
        if (this.isTraining) return;

        const episodes = parseInt(document.getElementById('trainingEpisodes').value);
        this.isTraining = true;

        const progressBar = document.getElementById('trainingProgress');
        const winRateDisplay = document.getElementById('winRate');

        let wins = 0;
        const winWindow = 100; // Calculate win rate over last 100 episodes
        const recentResults = [];

        for (let episode = 0; episode < episodes && this.isTraining; episode++) {
            // Reset game
            this.game.reset();
            let state = this.game.getStateRepresentation();
            let done = false;

            // Play episode
            while (!done) {
                const action = this.agent.getAction(state, true);
                const result = this.game.step(action);
                const nextState = this.game.getStateRepresentation();

                this.agent.update(state, action, result.reward, nextState, result.done);

                state = nextState;
                done = result.done;
            }

            // Record result
            recentResults.push(this.game.won ? 1 : 0);
            if (recentResults.length > winWindow) {
                recentResults.shift();
            }

            // Decay epsilon
            this.agent.decayEpsilon();

            // Update UI every 10 episodes
            if (episode % 10 === 0) {
                const progress = ((episode + 1) / episodes * 100).toFixed(0);
                progressBar.style.width = progress + '%';
                progressBar.textContent = progress + '%';

                const winRate = recentResults.reduce((a, b) => a + b, 0) / recentResults.length * 100;
                winRateDisplay.textContent = winRate.toFixed(1) + '%';

                // Allow UI to update
                await new Promise(resolve => setTimeout(resolve, 0));
            }

            // Render occasionally to show progress
            if (episode % 50 === 0) {
                this.render();
            }
        }

        // Training complete
        this.isTraining = false;
        progressBar.style.width = '100%';
        progressBar.textContent = '100%';

        // Save agent
        this.agent.save();

        alert(`Training complete! Episodes: ${episodes}\nFinal Epsilon: ${this.agent.epsilon.toFixed(4)}\nQ-table size: ${this.agent.qTable.size}`);

        // Reset game and render
        this.game.reset();
        this.render();
        this.updateUI();
    }

    stopTraining() {
        this.isTraining = false;
    }
}

// Initialize game controller
let gameController;

window.addEventListener('load', () => {
    gameController = new GameController();
});

// Global functions for button handlers
function resetGame() {
    if (gameController.isPlaying) {
        gameController.stopAI();
    }
    gameController.game.reset();
    gameController.render();
    gameController.updateUI();
    document.getElementById('statusMessage').style.display = 'none';
}

function setMode(mode) {
    if (gameController.isPlaying) {
        gameController.stopAI();
    }

    gameController.mode = mode;
    resetGame();

    if (mode === 'ai') {
        gameController.startAI();
    }
}

function trainAgent() {
    const trainingControls = document.getElementById('trainingControls');
    if (trainingControls.classList.contains('active')) {
        trainingControls.classList.remove('active');
    } else {
        trainingControls.classList.add('active');
    }
}

function startTraining() {
    if (gameController.isPlaying) {
        gameController.stopAI();
    }
    gameController.startTraining();
}

function stopTraining() {
    gameController.stopTraining();
}
