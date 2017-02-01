from py2neo import Graph
import matplotlib.pyplot as plt
from bokeh.io import output_file, show, gridplot
from bokeh.plotting import figure
import csv

# get handle to local neo4j instance
def get_connection_to_neo4j():
    graph = Graph(password='xxx')
    return graph

DATASETS_CSV='C:\\Users\\uday\\pycharm_projects\\network_analysis_web\\corrmut\\datasets.csv'
graph = get_connection_to_neo4j()
datasets_csv = open(DATASETS_CSV)

def read_datasets_csv():
    lines = csv.reader(datasets_csv)
    datasets = []
    for line in lines:
        dataset={}
        dataset['name']=line[0]
        dataset['no_of_strains']=line[1]
        dataset['comments']=line[2]
        datasets.append(dataset)
    return datasets
datasets = read_datasets_csv()

#get number of edges in the network for different cutoff values
def get_edge_counts_for_cutoffs(dataset):
    cutoffs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98]
    edge_counts = []
    for cutoff in cutoffs:
        query_part1 = 'MATCH (n:' + dataset
        query_part2 = ''')-[r]->(m)
        where toFloat(r.mic)>{cutoff}
        return count(r) as edges
        '''
        query = query_part1 + query_part2
        results = graph.data(query, cutoff=cutoff, dataset=dataset)
        edge_counts.append(results[0]['edges'])
    return cutoffs, edge_counts

# get number of nodes in the network for different cutoff values
def get_node_counts_for_cutoffs(dataset):
    cutoffs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98]
    node_counts = []
    for cutoff in cutoffs:
        query_part1 = 'MATCH (n:' + dataset
        query_part2 = ''')-[r]-(m)
        where toFloat(r.mic)>{cutoff}
        return count(distinct(n)) as nodes
        '''
        query = query_part1 + query_part2
        results = graph.data(query, cutoff=cutoff, dataset=dataset)
        node_counts.append(results[0]['nodes'])
    return cutoffs, node_counts

#simple line plot for plotting cutoff vs #edges
def plot_edgecounts_bokeh_line():
    output_file('bokeh_edgecount.html')
    datasets = get_datasets()
    plots = []
    for dataset in datasets:
        x,y=get_edge_counts_for_cutoffs(dataset=dataset)
        p = figure(title='edge counts for ' + dataset)
        p.left[0].formatter.use_scientific=False
        p.xaxis.axis_label='cut-off'
        p.yaxis.axis_label='# edges'
        p.line(x,y, color="green")
        plots.append(p)
    gp = gridplot(plots, ncols=2)
    show(gp)


#simple line plot of (x,y) using bokeh
def plot_nodecounts_bokeh_line():
    output_file('bokeh_nodecount.html')
    datasets = get_datasets()
    plots = []
    for dataset in datasets:
        x,y=get_node_counts_for_cutoffs(dataset=dataset)
        p = figure(title='node counts for ' + dataset)
        p.xaxis.axis_label='cut-off'
        p.yaxis.axis_label='# nodes'
        p.line(x,y, color="green")
        plots.append(p)
    gp = gridplot(plots, ncols=2)
    show(gp)

def draw_node_count_plot(cutoffs, node_counts):
    plt.plot(cutoffs, node_counts)
    plt.show()


def get_topN_nodes_with_topM_edges(n, m, dataset, cutoff):
    query_part1 = 'MATCH (n:' + dataset
    query_part2 = ''')-[r1]-()
    WHERE toFloat(r1.mic)>{cutoff}
    WITH n AS top_nodes, count(r1) AS NUM_CONNECTIONS ORDER BY NUM_CONNECTIONS desc LIMIT {n}
    MATCH (top_nodes)-[r2]-(m)
    WITH top_nodes, m, r2, NUM_CONNECTIONS ORDER BY r2.mic DESC
    RETURN top_nodes.protein + '_' + top_nodes.residue_number + ' (' + top_nodes.aa + ')' AS HIGHEST_DEGREE_RESIDUES,
    NUM_CONNECTIONS,
    COLLECT(m.protein+m.residue_number+' (' + m.aa + ')')[0..{m}] AS COVARYING_RESIDUES
    ORDER BY NUM_CONNECTIONS DESC
    '''
    query=query_part1+query_part2
    results = graph.data(query, n=n, m=m, cutoff=cutoff)
    return results


def get_datasets():
    query = """
    match (n) return collect(distinct labels(n)[1]) as labels
    """
    results = graph.data(query)
    labels = results[0]['labels']
    return labels


def get_topN_nodes(n):
    query = """
    MATCH (n1:HUMAN_ALL)-[r]-(n2)
    RETURN LABELS(n1)[0] AS PROTEIN, n1.residue_number AS RESIDUE_NUMBER, COUNT(r) as NUM_CONNECTIONS
    ORDER BY COUNT(r) DESC
    LIMIT {n}
    """
    results = graph.data(query, n=n)
    return results


def get_topN_edges(dataset, n):
    query_part1 = 'MATCH (n1:' + dataset
    query_part2 = ''')-[r]->(n2)
    RETURN n1.protein + '_' + n1.residue_number + ' (' + n1.aa + ')' as SOURCE,
    n2.protein + '_' + n2.residue_number + ' (' + n2.aa + ')' as TARGET,
    r.mic as MIC
    ORDER BY r.mic desc
    LIMIT {n}
    '''
    query = query_part1 + query_part2
    results = graph.data(query, n=n)
    return results


def search(protein, residue_number, dataset):
    query_part1 = 'MATCH (n:' + dataset
    query_part2 = ''')-[r] -(m)
    WHERE n.protein = {protein} and n.residue_number = {residue_number}
    RETURN
    n.protein + '_' + n.residue_number + ' (' + n.aa + ')' as SOURCE,
    m.protein + '_' + m.residue_number + ' (' + m.aa + ')' as TARGET,
    r.mic as MIC
    ORDER BY r.mic DESC
    LIMIT 10
    '''
    query = query_part1 + query_part2
    results = graph.data(query, protein=protein, residue_number=residue_number)
    return results

def get_topN_triplets(dataset):
    query_part1 = 'MATCH (n:' + dataset
    query_part2 = ''')-[r1]->(m)
    WITH distinct n, m, r1
    order by r1.mic desc
    LIMIT 10

    MATCH (m)-[r2]-(p)
    with distinct n, m, p, r1, r2

    MATCH (p)-[r3]-(n)
    return distinct
    n.protein + ' ' + n.residue_number as A,
    m.protein + ' ' + m.residue_number as B,
    p.protein + ' ' + p.residue_number as C,
    r1.mic as AB, r2.mic as BC, r3.mic as CA,
    toFloat(r1.mic) + toFloat(r2.mic) + toFloat(r3.mic) as total_mic
    order by total_mic desc
    LIMIT 40
    '''

    query = query_part1 + query_part2
    results = graph.data(query)
    return results

if __name__ == '__main__':
    search('HA', '100', 'AVIAN_H5_ALL')
    #get_topN_nodes_with_topM_edges(10,10,'HUMAN_ALL',0.5)
    #get_datasets()
    #x,y=get_node_counts_for_cutoffs('HUMAN_ALL')
    #print(get_topN_edges('HUMAN_ALL', 25))
    #plot_nodecounts_bokeh_line()
    #read_datasets_csv()
    #print(get_edge_counts_for_cutoffs('HUMAN_ALL'))
    #plot_edgecounts_bokeh_line()