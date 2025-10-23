// Q-Learning Agent Implementation in JavaScript

class QLearningAgent {
    constructor(options = {}) {
        this.nActions = options.nActions || 4;
        this.learningRate = options.learningRate || 0.1;
        this.discountFactor = options.discountFactor || 0.95;
        this.epsilon = options.epsilon || 1.0;
        this.epsilonMin = options.epsilonMin || 0.01;
        this.epsilonDecay = options.epsilonDecay || 0.995;

        // Q-table: maps state string -> array of Q-values for each action
        this.qTable = new Map();

        // Statistics
        this.totalEpisodes = 0;
        this.totalSteps = 0;
    }

    getQValues(state) {
        if (!this.qTable.has(state)) {
            this.qTable.set(state, new Array(this.nActions).fill(0));
        }
        return this.qTable.get(state);
    }

    getAction(state, training = true) {
        // Epsilon-greedy action selection
        if (training && Math.random() < this.epsilon) {
            // Explore: random action
            return Math.floor(Math.random() * this.nActions);
        } else {
            // Exploit: best known action
            const qValues = this.getQValues(state);
            const maxQ = Math.max(...qValues);

            // If multiple actions have same max Q, choose randomly among them
            const bestActions = [];
            for (let i = 0; i < qValues.length; i++) {
                if (qValues[i] === maxQ) {
                    bestActions.push(i);
                }
            }

            return bestActions[Math.floor(Math.random() * bestActions.length)];
        }
    }

    update(state, action, reward, nextState, done) {
        const qValues = this.getQValues(state);
        const currentQ = qValues[action];

        let targetQ;
        if (done) {
            targetQ = reward;
        } else {
            const nextQValues = this.getQValues(nextState);
            const maxNextQ = Math.max(...nextQValues);
            targetQ = reward + this.discountFactor * maxNextQ;
        }

        // Update Q-value
        qValues[action] = currentQ + this.learningRate * (targetQ - currentQ);
    }

    decayEpsilon() {
        this.epsilon = Math.max(this.epsilonMin, this.epsilon * this.epsilonDecay);
        this.totalEpisodes++;
    }

    save() {
        // Save to localStorage
        const data = {
            qTable: Array.from(this.qTable.entries()),
            epsilon: this.epsilon,
            totalEpisodes: this.totalEpisodes,
            totalSteps: this.totalSteps,
            learningRate: this.learningRate,
            discountFactor: this.discountFactor,
            epsilonMin: this.epsilonMin,
            epsilonDecay: this.epsilonDecay,
            nActions: this.nActions
        };
        localStorage.setItem('qLearningAgent', JSON.stringify(data));
        console.log('Agent saved to localStorage');
    }

    load() {
        const data = localStorage.getItem('qLearningAgent');
        if (!data) {
            console.log('No saved agent found');
            return false;
        }

        const parsed = JSON.parse(data);

        // Restore Q-table
        this.qTable = new Map(parsed.qTable);

        // Restore parameters
        this.epsilon = parsed.epsilon;
        this.totalEpisodes = parsed.totalEpisodes;
        this.totalSteps = parsed.totalSteps;
        this.learningRate = parsed.learningRate;
        this.discountFactor = parsed.discountFactor;
        this.epsilonMin = parsed.epsilonMin;
        this.epsilonDecay = parsed.epsilonDecay;
        this.nActions = parsed.nActions;

        console.log('Agent loaded from localStorage');
        console.log(`Episodes trained: ${this.totalEpisodes}`);
        console.log(`Current epsilon: ${this.epsilon.toFixed(4)}`);
        console.log(`Q-table size: ${this.qTable.size} states`);

        return true;
    }

    reset() {
        this.qTable.clear();
        this.epsilon = 1.0;
        this.totalEpisodes = 0;
        this.totalSteps = 0;
        console.log('Agent reset');
    }

    getStats() {
        return {
            totalEpisodes: this.totalEpisodes,
            totalSteps: this.totalSteps,
            epsilon: this.epsilon,
            qTableSize: this.qTable.size
        };
    }
}
