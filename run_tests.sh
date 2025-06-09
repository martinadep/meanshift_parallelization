#!/bin/bash

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
    
    # Crea un file per questo numero di thread
    result_file="results/main_matrix_${t}_threads.txt"
    echo "# Results for $t threads" > "$result_file"
    
    # Ciclo sulle ripetizioni
    for r in $(seq 1 $repetitions); do
        echo "  Esecuzione $r/$repetitions..."
        
        # Imposta variabile d'ambiente per numero di thread
        export OMP_NUM_THREADS=$t
        
        # Esegui il programma e salva l'output nel file
        echo "## Run $r" >> "$result_file"
        ./build/main_matrix >> "$result_file"
        echo "" >> "$result_file"  # Aggiungi una riga vuota tra i runs
    done
done

echo "Test completati!"
echo "Per visualizzare i risultati, esegui: python py_utils/plot_results.py"