#!/bin/bash
# filepath: run_tests.sh

# Array dei numeri di thread da testare
threads=(1 2 4 8 16 32 64)
# Numero di ripetizioni per ogni configurazione
repetitions=5

# Crea directory per i risultati se non esiste
mkdir -p results

echo "Inizio dei test di main_matrix..."

# Ciclo sui numeri di thread
for t in "${threads[@]}"; do
    echo "Esecuzione test con $t thread..."
    
    # Ciclo sulle ripetizioni
    for r in $(seq 1 $repetitions); do
        echo "  Esecuzione $r/$repetitions..."
        
        # Esegui il programma e salva l'output
        ./build/main_matrix $t > "results/output_${t}_threads_run_${r}.txt"
    done
done

echo "Test completati!"
echo "Generazione script di visualizzazione..."
