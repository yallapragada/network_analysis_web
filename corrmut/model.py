from py2neo import Graph
import csv
import socket

topN_csv_folder = 'C:\\uday\\gmu\\correlations\\results\\10proteins\\topN_csv'

# get handle to local neo4j instance
def get_connection_to_neo4j():
    graph = Graph(password='flu')
    return graph

if socket.gethostname() == 'omics':
    DATASETS_CSV='/home/uyallapr/network_analysis_web/corrmut/datasets.csv'
else:
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


def get_topN_nodes_with_topM_edges(n, m, dataset, cutoff):
    query_part1 = 'MATCH (n:' + dataset
    query_part2 = ''')-[r1]-()
    WHERE toFloat(r1.mic)>{cutoff}
    WITH n AS top_nodes, count(r1) AS NUM_CONNECTIONS
    ORDER BY NUM_CONNECTIONS desc
    LIMIT {n}
    MATCH (top_nodes)-[r2]-(m)
    WITH top_nodes, m, r2, NUM_CONNECTIONS
    ORDER BY r2.mic DESC
    RETURN top_nodes.protein + '_' + top_nodes.residue_number + ' (' + top_nodes.aa + ')' AS HIGHEST_DEGREE_RESIDUES,
    NUM_CONNECTIONS,
    COLLECT(m.protein+m.residue_number+' (' + m.aa + ')')[0..{m}] AS COVARYING_RESIDUES
    ORDER BY NUM_CONNECTIONS DESC
    '''
    query=query_part1+query_part2
    results = graph.data(query, n=n, m=m, cutoff=cutoff)
    csv_file = topN_csv_folder + '\\' + dataset + '_nodes.csv'

    with open(csv_file, 'w', newline='') as out_file:

        headers = ['HIGHEST_DEGREE_RESIDUES', 'NUM_CONNECTIONS', 'COVARYING_RESIDUES']
        csv_data = [headers]
        for result in results:
            csv_data.append([result[h] for h in headers])

        writer = csv.writer(out_file)
        writer.writerows(csv_data)

    return results


def get_topN_nodes(dataset, n):
    query_part1 = 'MATCH (n1:' + dataset
    query_part2 = ''')-[r]-(n2)
    WHERE toFloat(r.mic) > 0.5
    RETURN LABELS(n1)[0] AS PROTEIN, n1.residue_number AS RESIDUE_NUMBER, n1.aa AS AMINO_ACID, COUNT(r) as NUM_CONNECTIONS
    ORDER BY COUNT(r) DESC
    LIMIT {n}
    '''
    query = query_part1 + query_part2
    results = graph.data(query, n=n)
    return results


def get_topN_edges(dataset, n):
    query_part1 = 'MATCH (n1:' + dataset
    query_part2 = ''')-[r]->(n2)
    WHERE toFloat(r.mic) > 0.5
    RETURN n1.protein + '_' + n1.residue_number + ' (' + n1.aa + ')' as SOURCE,
    n2.protein + '_' + n2.residue_number + ' (' + n2.aa + ')' as TARGET,
    r.mic as MIC
    ORDER BY r.mic desc
    LIMIT {n}
    '''
    query = query_part1 + query_part2
    results = graph.data(query, n=n)

    csv_file = topN_csv_folder + '\\' + dataset + '_edges.csv'

    with open(csv_file, 'w', newline='') as out_file:

        headers = ['SOURCE', 'TARGET', 'MIC']
        csv_data = [headers]
        for result in results:
            csv_data.append([result[h] for h in headers])

        writer = csv.writer(out_file)
        writer.writerows(csv_data)

    return results


def search(protein, residue_number, dataset):
    query_part1 = 'MATCH (n:' + dataset
    query_part2 = ''')-[r] -(m)
    WHERE n.protein = {protein} and n.residue_number = {residue_number} and toFloat(r.mic) > 0.5
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
    print('do nothing')
    #search('HA', '100', 'AVIAN_H5_ALL')
    #get_topN_nodes_with_topM_edges(10,10,'HUMAN_ALL',0.5)
    #x,y=get_node_counts_for_cutoffs('HUMAN_ALL')
    #print(get_topN_edges('HUMAN_ALL', 25))
    #read_datasets_csv()
    #print(get_edge_counts_for_cutoffs('HUMAN_ALL'))