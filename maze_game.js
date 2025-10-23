// Maze Game Implementation in JavaScript

class MazeGame {
    // Action constants
    static UP = 0;
    static DOWN = 1;
    static LEFT = 2;
    static RIGHT = 3;
    static ACTIONS = [MazeGame.UP, MazeGame.DOWN, MazeGame.LEFT, MazeGame.RIGHT];

    // Cell types
    static EMPTY = 0;
    static WALL = 1;
    static COIN = 2;
    static EXIT = 3;

    constructor(mazeSize = {height: 10, width: 10}, numCoins = 5) {
        this.height = mazeSize.height;
        this.width = mazeSize.width;
        this.numCoins = numCoins;
        this.reset();
    }

    reset() {
        // Create maze
        this.maze = this._createMaze();

        // Place player at top-left area
        this.playerPos = {row: 1, col: 1};

        // Place exit at bottom-right area
        this.exitPos = {row: this.height - 2, col: this.width - 2};
        this.maze[this.exitPos.row][this.exitPos.col] = MazeGame.EXIT;

        // Place NPC far from player for easier gameplay
        this.npcPos = this._getRandomEmptyPos(8);

        // Place coins
        this.coins = [];
        for (let i = 0; i < this.numCoins; i++) {
            const coinPos = this._getRandomEmptyPos();
            this.coins.push(coinPos);
            this.maze[coinPos.row][coinPos.col] = MazeGame.COIN;
        }

        this.score = 0;
        this.steps = 0;
        this.maxSteps = 500;
        this.caught = false;
        this.won = false;

        return this.getState();
    }

    _createMaze() {
        // Initialize empty maze
        const maze = Array(this.height).fill(0).map(() => Array(this.width).fill(MazeGame.EMPTY));

        // Border walls
        for (let i = 0; i < this.width; i++) {
            maze[0][i] = MazeGame.WALL;
            maze[this.height - 1][i] = MazeGame.WALL;
        }
        for (let i = 0; i < this.height; i++) {
            maze[i][0] = MazeGame.WALL;
            maze[i][this.width - 1] = MazeGame.WALL;
        }

        // Add internal walls (reduced density for more escape routes)
        if (this.width > 6) {
            for (let i = 2; i < this.height - 2; i += 3) {
                for (let j = 1; j < this.width / 2; j++) {
                    if (Math.random() < 0.25) {  // Reduced from 0.6 to 0.25 for more open space
                        maze[i][j * 2] = MazeGame.WALL;
                    }
                }
            }
        }

        if (this.height > 6) {
            for (let i = 1; i < this.height / 2; i++) {
                for (let j = 2; j < this.width - 2; j += 3) {
                    if (Math.random() < 0.25) {  // Reduced from 0.6 to 0.25 for more open space
                        maze[i * 2][j] = MazeGame.WALL;
                    }
                }
            }
        }

        return maze;
    }

    _getRandomEmptyPos(minDistanceFromPlayer = 0) {
        while (true) {
            const row = Math.floor(Math.random() * (this.height - 2)) + 1;
            const col = Math.floor(Math.random() * (this.width - 2)) + 1;

            if (this.maze[row][col] === MazeGame.EMPTY) {
                if (minDistanceFromPlayer > 0) {
                    const distance = Math.abs(row - this.playerPos.row) +
                                   Math.abs(col - this.playerPos.col);
                    if (distance >= minDistanceFromPlayer) {
                        return {row, col};
                    }
                } else {
                    return {row, col};
                }
            }
        }
    }

    getState() {
        return {
            playerPos: {...this.playerPos},
            npcPos: {...this.npcPos},
            coins: this.coins.map(c => ({...c})),
            score: this.score,
            steps: this.steps,
            caught: this.caught,
            won: this.won,
            maze: this.maze.map(row => [...row])
        };
    }

    step(action) {
        if (this.caught || this.won) {
            return {state: this.getState(), reward: 0, done: true};
        }

        // Move player
        const newPos = this._getNewPosition(this.playerPos, action);
        if (this._isValidMove(newPos)) {
            this.playerPos = newPos;
        }

        let reward = -0.1; // Small penalty for each step

        // Check coin collection
        for (let i = 0; i < this.coins.length; i++) {
            if (this.coins[i].row === this.playerPos.row &&
                this.coins[i].col === this.playerPos.col) {
                this.coins.splice(i, 1);
                this.maze[this.playerPos.row][this.playerPos.col] = MazeGame.EMPTY;
                this.score += 10;
                reward += 10;
                break;
            }
        }

        // Check if reached exit
        if (this.playerPos.row === this.exitPos.row &&
            this.playerPos.col === this.exitPos.col) {
            this.won = true;
            reward += 100;
            return {state: this.getState(), reward: reward, done: true};
        }

        // Move NPC
        this._moveNPC();

        // Check if caught
        if (this.playerPos.row === this.npcPos.row &&
            this.playerPos.col === this.npcPos.col) {
            this.caught = true;
            reward -= 50;
            return {state: this.getState(), reward: reward, done: true};
        }

        this.steps++;

        // Check max steps
        if (this.steps >= this.maxSteps) {
            reward -= 10;
            return {state: this.getState(), reward: reward, done: true};
        }

        return {state: this.getState(), reward: reward, done: false};
    }

    _getNewPosition(pos, action) {
        const newPos = {...pos};
        switch (action) {
            case MazeGame.UP:
                newPos.row--;
                break;
            case MazeGame.DOWN:
                newPos.row++;
                break;
            case MazeGame.LEFT:
                newPos.col--;
                break;
            case MazeGame.RIGHT:
                newPos.col++;
                break;
        }
        return newPos;
    }

    _isValidMove(pos) {
        if (pos.row < 0 || pos.row >= this.height ||
            pos.col < 0 || pos.col >= this.width) {
            return false;
        }
        return this.maze[pos.row][pos.col] !== MazeGame.WALL;
    }

    _moveNPC() {
        // NPC only moves 30% of the time to make it easier to avoid
        if (Math.random() > 0.3) {
            return;
        }

        // Random movement: NPC moves in random valid directions
        const validActions = [];

        for (const action of MazeGame.ACTIONS) {
            const newPos = this._getNewPosition(this.npcPos, action);
            if (this._isValidMove(newPos)) {
                validActions.push(action);
            }
        }

        // Move NPC to a random valid position
        if (validActions.length > 0) {
            const action = validActions[Math.floor(Math.random() * validActions.length)];
            this.npcPos = this._getNewPosition(this.npcPos, action);
        }
    }

    getStateRepresentation() {
        // Compact state representation for Q-learning
        const npcRelative = {
            row: this.npcPos.row - this.playerPos.row,
            col: this.npcPos.col - this.playerPos.col
        };

        const exitRelative = {
            row: this.exitPos.row - this.playerPos.row,
            col: this.exitPos.col - this.playerPos.col
        };

        let coinRelative = {row: 0, col: 0};
        if (this.coins.length > 0) {
            // Find nearest coin
            let minDist = Infinity;
            for (const coin of this.coins) {
                const dist = Math.abs(coin.row - this.playerPos.row) +
                           Math.abs(coin.col - this.playerPos.col);
                if (dist < minDist) {
                    minDist = dist;
                    coinRelative = {
                        row: coin.row - this.playerPos.row,
                        col: coin.col - this.playerPos.col
                    };
                }
            }
        }

        // Return string representation for dictionary key
        return JSON.stringify({
            player: this.playerPos,
            npc: npcRelative,
            exit: exitRelative,
            coin: coinRelative,
            coinsLeft: this.coins.length
        });
    }
}
