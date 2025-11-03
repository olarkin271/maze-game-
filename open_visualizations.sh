#!/bin/bash
# Script to open all training visualizations

cd /home/user/maze-game-/visualizations

echo "Opening all training visualizations..."
echo ""
echo "Files being opened:"
echo "1. training_dashboard.png"
echo "2. q_value_heatmap.png"
echo "3. q_value_evolution.png"
echo "4. performance_distributions.png"
echo "5. learning_phases.png"
echo ""

# Try to open with system default image viewer
if command -v open &> /dev/null; then
    # macOS
    open training_dashboard.png
    open q_value_heatmap.png
    open q_value_evolution.png
    open performance_distributions.png
    open learning_phases.png
    echo "✓ Images opened in default viewer (Mac)"
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open training_dashboard.png
    xdg-open q_value_heatmap.png
    xdg-open q_value_evolution.png
    xdg-open performance_distributions.png
    xdg-open learning_phases.png
    echo "✓ Images opened in default viewer (Linux)"
elif command -v start &> /dev/null; then
    # Windows
    start training_dashboard.png
    start q_value_heatmap.png
    start q_value_evolution.png
    start performance_distributions.png
    start learning_phases.png
    echo "✓ Images opened in default viewer (Windows)"
else
    echo "❌ Could not detect system. Please open files manually from:"
    echo "   /home/user/maze-game-/visualizations/"
fi
