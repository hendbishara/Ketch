import pandas as pd
import numpy as np
import time
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from Dijkstra import Modified_Dijkstra  


# Define a dummy Cluster class to simulate the clusters used in your algorithm
class Cluster:
    def __init__(self, cluster_id, coordinates, capacity):
        self.id = cluster_id
        self.coordinates = coordinates
        self.capacity = capacity

class AlgorithmAnalyzer:
    def __init__(self, warehouse_coords: Tuple[float, float]):
        self.versions = ["Base", "V1", "V2", "V3"]
        self.warehouse_coords = warehouse_coords
        self.results = {
            'version': [],
            'num_clusters': [],
            'max_capacity': [],
            'run_number': [],
            'num_orders': [],
            'avg_path_loss': [],
            'total_path_loss': [],
            'avg_node_loss': [],
            'runtime': []
        }
    
    def run_single_experiment(self, 
                            clusters: List, 
                            max_capacity: int, 
                            version: str) -> Dict:
        """Run a single experiment for a given version and configuration"""
        start_time = time.time()
        
        # Initialize algorithm
        algo = Modified_Dijkstra(clusters, max_capacity, self.warehouse_coords, version)
        
        # Get orders and metrics
        orders = algo.get_orders()
        orders_loss = algo.get_orders_loss()
        
        runtime = time.time() - start_time
        
        return {
            'num_orders': len(orders),
            'avg_path_loss': np.mean(orders_loss) if orders_loss else 0,
            'total_path_loss': np.sum(orders_loss) if orders_loss else 0,
            'avg_node_loss': algo.get_Avg_loss_on_nodes(),
            'runtime': runtime
        }
    
    def run_experiments(self, 
                       cluster_sizes: List[int],
                       max_capacities: List[int],
                       num_runs: int = 20):
        """Run experiments across all configurations"""
        for n_clusters in cluster_sizes:
            for max_capacity in max_capacities:
                for run in range(num_runs):
                    # Generate random clusters here
                    # You'll need to implement this based on your cluster structure
                    clusters = self.generate_random_clusters(n_clusters)
                    
                    for version in self.versions:
                        results = self.run_single_experiment(
                            clusters, max_capacity, version)
                        
                        # Store results
                        self.results['version'].append(version)
                        self.results['num_clusters'].append(n_clusters)
                        self.results['max_capacity'].append(max_capacity)
                        self.results['run_number'].append(run)
                        self.results['num_orders'].append(results['num_orders'])
                        self.results['avg_path_loss'].append(results['avg_path_loss'])
                        self.results['total_path_loss'].append(results['total_path_loss'])
                        self.results['avg_node_loss'].append(results['avg_node_loss'])
                        self.results['runtime'].append(results['runtime'])
    
    def generate_random_clusters(self, n_clusters: int) -> List:
        """
        Generate random clusters for testing
        Implement this based on your cluster structure
        """
        # This is a placeholder - implement based on your cluster class structure
        clusters = []
        for i in range(n_clusters):
            # Create random coordinates within reasonable bounds
            lat = np.random.uniform(30, 50)
            lon = np.random.uniform(-100, -80)
            capacity = np.random.uniform(10, 100)
            # Create cluster object with your structure
            cluster = Cluster(f"C{i}", (lat, lon), capacity)
            clusters.append(cluster)
        return clusters
    
    def get_results_df(self) -> pd.DataFrame:
        """Convert results to DataFrame"""
        return pd.DataFrame(self.results)
    
    def plot_comparative_analysis(self,save_pdf: bool = False, pdf_filename: str = 'analysis_plots.pdf'):
        """
        Create comparative visualization plots
        
        Parameters:
        save_pdf (bool): Whether to save the plots to PDF
        pdf_filename (str): Name of the PDF file to save
        
        Returns:
        matplotlib.figure.Figure: The generated figure
        """
        df = self.get_results_df()
        
        # Create figure with multiple subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Algorithm Version Comparison', fontsize=16)
        
        # Runtime comparison
        sns.boxplot(data=df, x='version', y='runtime', ax=axes[0,0])
        axes[0,0].set_title('Runtime Distribution by Version')
        axes[0,0].set_ylabel('Runtime (seconds)')
        
        # Average path loss comparison
        sns.boxplot(data=df, x='version', y='avg_path_loss', ax=axes[0,1])
        axes[0,1].set_title('Average Path Loss by Version')
        axes[0,1].set_ylabel('Average Path Loss')
        
        # Scatter plot of runtime vs number of clusters
        for version in self.versions:
            version_data = df[df['version'] == version]
            axes[1,0].scatter(version_data['num_clusters'], 
                            version_data['runtime'], 
                            label=version, alpha=0.5)
        axes[1,0].set_title('Runtime vs Number of Clusters')
        axes[1,0].set_xlabel('Number of Clusters')
        axes[1,0].set_ylabel('Runtime (seconds)')
        axes[1,0].legend()
        
        # Average node loss comparison
        sns.boxplot(data=df, x='version', y='avg_node_loss', ax=axes[1,1])
        axes[1,1].set_title('Average Node Loss by Version')
        axes[1,1].set_ylabel('Average Node Loss')
        
        plt.tight_layout()
        
        # Save to PDF if requested
        if save_pdf:
            fig.savefig(pdf_filename, format='pdf', bbox_inches='tight', dpi=300)
            print(f"Plots saved to {pdf_filename}")
        
        return fig
    
    def generate_summary_tables(self) -> Dict[str, pd.DataFrame]:
        """Generate summary statistics tables"""
        df = self.get_results_df()
        
        # Calculate mean metrics by version
        mean_metrics = df.groupby('version').agg({
            'runtime': ['mean', 'std'],
            'avg_path_loss': ['mean', 'std'],
            'avg_node_loss': ['mean', 'std'],
            'num_orders': ['mean', 'std']
        }).round(3)
        
        # Calculate mean metrics by version and cluster size
        cluster_metrics = df.groupby(['version', 'num_clusters']).agg({
            'runtime': 'mean',
            'avg_path_loss': 'mean',
            'avg_node_loss': 'mean'
        }).round(3)
        
        return {
            'overall_summary': mean_metrics,
            'cluster_summary': cluster_metrics
        }
    def save_to_excel(self, filename: str):
        """
        Save all results and summary tables to an Excel file
        Each table will be saved in a separate worksheet
        
        Parameters:
        filename (str): Name of the Excel file (e.g., 'algorithm_results.xlsx')
        """
        try:
            # Create Excel writer object
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Save detailed results
                df = self.get_results_df()
                df.to_excel(writer, sheet_name='Detailed Results', index=False)
                
                # Get summary tables
                summary_tables = self.generate_summary_tables()
                
                # Save overall summary
                summary_tables['overall_summary'].to_excel(writer, sheet_name='Overall Summary')
                
                # Save cluster summary
                summary_tables['cluster_summary'].to_excel(writer, sheet_name='Cluster Summary')
                
                # Create summary by max capacity
                capacity_summary = df.groupby(['version', 'max_capacity']).agg({
                    'runtime': ['mean', 'std'],
                    'avg_path_loss': ['mean', 'std'],
                    'avg_node_loss': ['mean', 'std'],
                    'num_orders': ['mean', 'std']
                }).round(3)
                capacity_summary.to_excel(writer, sheet_name='Capacity Summary')
                
                # Create pivot table for comprehensive view
                pivot_table = pd.pivot_table(df,
                    values=['runtime', 'avg_path_loss', 'avg_node_loss', 'num_orders'],
                    index=['version', 'num_clusters', 'max_capacity'],
                    aggfunc=['mean', 'std']
                ).round(3)
                pivot_table.to_excel(writer, sheet_name='Pivot Analysis')
                
            print(f"Results successfully saved to {filename}")
            
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            raise


# Example usage:
if __name__ == "__main__":
    # Define test parameters
    warehouse_coords = (40.7128, -74.0060)  # Example coordinates
    cluster_sizes = [10, 20, 30, 40, 50]
    max_capacities = [100, 200, 300]
    
    # Initialize analyzer
    analyzer = AlgorithmAnalyzer(warehouse_coords)
    
    # Run experiments
    analyzer.run_experiments(cluster_sizes, max_capacities)
    
    # Generate visualizations
    fig = analyzer.plot_comparative_analysis(save_pdf=True, pdf_filename='algorithm_analysis.pdf')
    plt.show()
    
    # Generate summary tables
    summary_tables = analyzer.generate_summary_tables()
    print("\nOverall Summary:")
    print(summary_tables['overall_summary'])
    print("\nCluster Size Summary:")
    print(summary_tables['cluster_summary'])
    
    #save tables to excel
    analyzer.save_to_excel("algorithm_analysis_results.xlsx")