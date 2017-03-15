from corrmut import app
from flask import render_template, request
import model as model
import collections

@app.route('/search', methods=['GET','POST'])
def search():
    return render_template('search.html')

@app.route('/search_results', methods=['GET','POST'])
def search_results():
    protein         = request.form['protein']
    residue_number  = request.form['residue_number']
    dataset         = request.form['dataset']
    top_10_edges    = model.search(protein=protein, residue_number=residue_number, dataset=dataset)
    return render_template('search_results.html', top_10_edges=top_10_edges, protein=protein, residue_number=residue_number, dataset=dataset)

@app.route('/')
def homepage():
    datasets=model.datasets
    return render_template('dashboard.html', datasets=datasets)

@app.route('/main')
def main():
    datasets=model.datasets
    return render_template('dashboard.html', datasets=datasets)

@app.route('/node_counts')
def node_counts():
    return render_template('nodecounts.html')

@app.route('/edge_counts')
def edge_counts():
    return render_template('edgecounts.html')

@app.route('/topN_edges')
def topN_edges():
    top_25_edges_dict = {}
    datasets = sorted([dataset['name'] for dataset in model.datasets])
    for dataset in datasets:
        top_25_edges = model.get_topN_edges(dataset=dataset, n=25)
        top_25_edges_dict[dataset] = top_25_edges
    top_25_edges_dict_ordered = collections.OrderedDict(sorted(top_25_edges_dict.items()))
    return render_template('topNedges.html', top_25_edges_dict=top_25_edges_dict_ordered)

@app.route('/topN_nodes', methods=['GET','POST'])
def topN_nodes():
    top_25_nodes_dict = {}
    datasets = sorted([dataset['name'] for dataset in model.datasets])
    for dataset in datasets:
        top_25_nodes = model.get_topN_nodes_with_topM_edges(25, 10, dataset=dataset, cutoff=0.5)
        top_25_nodes_dict[dataset] = top_25_nodes
    top_25_nodes_dict_ordered = collections.OrderedDict(sorted(top_25_nodes_dict.items()))
    return render_template('topNnodes.html', top_25_nodes_dict=top_25_nodes_dict_ordered)

@app.route('/topN_triplets', methods=['GET', 'POST'])
def topN_triplets():
    top40_triplets_dict = {}
    datasets = sorted([dataset['name'] for dataset in model.datasets])
    for dataset in datasets:
        top_40_triplets = model.get_topN_triplets(dataset=dataset)
        top40_triplets_dict[dataset] = top_40_triplets
    return render_template('topNtriplets.html', top40_triplets_dict=top40_triplets_dict)

@app.route('/dviz', methods=['GET', 'POST'])
def dviz():
    return render_template('dviz.html')

@app.route('/macro', methods=['GET', 'POST'])
def macro():
    return render_template('macro.html')

@app.route('/mic', methods=['GET', 'POST'])
def mic():
    return render_template('mic.html')

@app.route('/degree_dist', methods=['GET', 'POST'])
def degree_dist():
    return render_template('degree.html')

@app.route('/clustering_dist', methods=['GET', 'POST'])
def clustering_dist():
    return render_template('clustering.html')

@app.route('/entropy_dist', methods=['GET', 'POST'])
def entropy():
    return render_template('entropy.html')