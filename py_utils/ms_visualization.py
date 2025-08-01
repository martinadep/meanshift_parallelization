import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from sklearn.datasets import make_blobs
from sklearn.cluster import MeanShift
import seaborn as sns

# Configurazione minimal con sfondo bianco
plt.style.use('default')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
plt.rcParams['font.size'] = 11

class MeanShiftVisualizer:
    def __init__(self, bandwidth=2.0):
        self.bandwidth = bandwidth
        self.data = None
        self.centers_history = []
        
    def generate_data(self, n_samples=300, n_centers=4, cluster_std=1.5, random_state=42):
        """Genera dati di esempio per il clustering"""
        self.data, _ = make_blobs(
            n_samples=n_samples, 
            centers=n_centers, 
            cluster_std=cluster_std,
            random_state=random_state
        )
        return self.data
    
    def manual_mean_shift_step(self, points, centers, bandwidth):
        """Un singolo step dell'algoritmo Mean Shift"""
        new_centers = []
        
        for center in centers:
            # Calcola le distanze da questo centro
            distances = np.linalg.norm(points - center, axis=1)
            
            # Trova i punti dentro la finestra (kernel gaussiano)
            weights = np.exp(-(distances**2) / (2 * bandwidth**2))
            
            # Calcola il nuovo centro come media pesata
            if np.sum(weights) > 0:
                new_center = np.average(points, axis=0, weights=weights)
                new_centers.append(new_center)
            else:
                new_centers.append(center)
                
        return np.array(new_centers)
    
    def run_mean_shift_animation(self, max_iterations=20):
        """Esegue Mean Shift e salva la storia per l'animazione"""
        # Inizializza i centri casualmente
        n_centers = 8
        x_min, x_max = self.data[:, 0].min() - 1, self.data[:, 0].max() + 1
        y_min, y_max = self.data[:, 1].min() - 1, self.data[:, 1].max() + 1
        
        centers = np.random.uniform(
            low=[x_min, y_min], 
            high=[x_max, y_max], 
            size=(n_centers, 2)
        )
        
        self.centers_history = [centers.copy()]
        
        for i in range(max_iterations):
            new_centers = self.manual_mean_shift_step(self.data, centers, self.bandwidth)
            self.centers_history.append(new_centers.copy())
            
            # Controlla convergenza
            if np.allclose(centers, new_centers, atol=0.01):
                print(f"Convergence reached after {i+1} iterations")
                break
                
            centers = new_centers
            
        return self.centers_history
    
    def plot_static_comparison(self):
        """Crea un grafico statico che mostra prima/dopo"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot iniziale
        ax1.scatter(self.data[:, 0], self.data[:, 1], alpha=0.7, s=50)
        ax1.scatter(self.centers_history[0][:, 0], self.centers_history[0][:, 1], 
                   c='red', marker='x', s=200, linewidths=3, label='Centri iniziali')
        ax1.set_title('Stato Iniziale', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot finale
        final_centers = self.centers_history[-1]
        ax2.scatter(self.data[:, 0], self.data[:, 1], alpha=0.7, s=50)
        ax2.scatter(final_centers[:, 0], final_centers[:, 1], 
                   c='red', marker='o', s=200, linewidths=2, 
                   edgecolors='black', label='Centri finali')
        
        # Aggiungi cerchi per mostrare il bandwidth
        for center in final_centers:
            circle = plt.Circle(center, self.bandwidth, fill=False, 
                              color='red', alpha=0.3, linestyle='--')
            ax2.add_patch(circle)
            
        ax2.set_title('Risultato Finale', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('mean_shift_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_sklearn_comparison(self):
        """Confronta con l'implementazione di scikit-learn"""
        ms = MeanShift(bandwidth=self.bandwidth)
        ms.fit(self.data)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot dei dati colorati per cluster
        labels = ms.labels_
        colors = plt.cm.tab10(labels)
        ax.scatter(self.data[:, 0], self.data[:, 1], c=colors, alpha=0.7, s=50)
        
        # Plot dei centri finali
        centers = ms.cluster_centers_
        ax.scatter(centers[:, 0], centers[:, 1], 
                  c='red', marker='o', s=300, linewidths=3,
                  edgecolors='black', label=f'Cluster Centers ({len(centers)})')
        
        # Aggiungi cerchi per il bandwidth
        for center in centers:
            circle = plt.Circle(center, self.bandwidth, fill=False, 
                              color='red', alpha=0.3, linestyle='--')
            ax.add_patch(circle)
        
        ax.set_title('Mean Shift Clustering (Scikit-learn)', 
                    fontsize=16, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.savefig('mean_shift_sklearn.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Numero di cluster trovati: {len(centers)}")
    
    def create_step_by_step_plot(self, steps_to_show=5):
        """Create a minimal plot showing the first N steps of the algorithm"""
        n_steps = min(steps_to_show, len(self.centers_history))
        
        # Colori minimal con tonalità blu
        data_color = '#4A90E2'  # Blu elegante per i dati
        center_color = '#1E3A8A'  # Blu scuro per i centri
        arrow_color = '#6B7280'  # Grigio per le frecce
        
        fig, axes = plt.subplots(1, n_steps, figsize=(4*n_steps, 6))
        fig.patch.set_facecolor('white')
        
        if n_steps == 1:
            axes = [axes]
        
        for i in range(n_steps):
            ax = axes[i]
            ax.set_facecolor('white')
            
            # Plot dei dati - stile minimal
            ax.scatter(self.data[:, 0], self.data[:, 1], 
                      c=data_color, alpha=0.6, s=25, 
                      edgecolors='none')
            
            # Plot dei centri - minimal e pulito
            centers = self.centers_history[i]
            ax.scatter(centers[:, 0], centers[:, 1], 
                      c=center_color, marker='o', s=80, 
                      linewidths=1.5, edgecolors='white', 
                      alpha=0.9, zorder=5)
            
            # Frecce minimal per mostrare il movimento
            if i > 0:
                prev_centers = self.centers_history[i-1]
                for j in range(len(centers)):
                    if j < len(prev_centers):
                        ax.annotate('', xy=centers[j], xytext=prev_centers[j],
                                  arrowprops=dict(arrowstyle='->', 
                                                color=arrow_color, 
                                                lw=3, alpha=0.7,
                                                shrinkA=8, shrinkB=8))
            
            # Styling minimal e pulito
            ax.set_title(f'iteration {i+1}', fontweight='normal', 
                        color='black', fontsize=17)
            
            # Griglia minimal
            ax.grid(True, alpha=0.3, color='gray', linewidth=0.5, linestyle='-')
            ax.set_axisbelow(True)
            
            # Bordi standard
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            
            ax.tick_params(colors='black', labelsize=10)
            
            # Etichette assi minimal
            if i == 0:
                ax.set_ylabel('Y coordinate', fontsize=14)
            ax.set_xlabel('X coordinate', fontsize=14)
            
        # # Titolo generale minimal
        # fig.suptitle('Mean Shift Algorithm Evolution', 
        #             fontsize=15, fontweight='normal', color='black')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)
        plt.savefig('mean_shift_steps_minimal.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.savefig('mean_shift_steps_minimal.pdf')
        plt.show()

def main():
    """Main function to run all visualizations"""
    print("🎯 Generating Mean Shift visualizations for thesis")
    print("=" * 50)
    
    # Create the visualizer
    viz = MeanShiftVisualizer(bandwidth=2.5)
    
    # Generate data
    print("📊 Generating sample data...")
    data = viz.generate_data(n_samples=300, n_centers=4)
    print(f"   Generated {len(data)} data points")
    
    # Run Mean Shift
    print("🔄 Running Mean Shift algorithm...")
    history = viz.run_mean_shift_animation()
    print(f"   Completed in {len(history)} iterations")
    
    # Create visualizations
    print("🎨 Creating visualizations...")
    
    
    print("   2. Modern step-by-step visualization...")
    viz.create_step_by_step_plot(steps_to_show=4)
    
    
    print("\n✅ Completed! Files saved:")
    print("   - mean_shift_comparison.png")
    print("   - mean_shift_steps_modern.png") 
    print("   - mean_shift_sklearn.png")
    
    print("\n💡 Tip: Modify bandwidth, n_samples, n_centers")
    print("   parameters to get different visualizations!")

if __name__ == "__main__":
    main()