from corrmut import app
from flask import render_template, request
import model as model

@app.route('/search', methods=['GET','POST'])
def search():
    return render_template('search.html')

@app.route('/search_results', methods=['GET','POST'])
def search_results():
    protein = request.form['protein']
    residue_number = request.form['residue_number']
    top_10_edges_dict = {}
    datasets = model.get_datasets()
    for dataset in datasets:
        top_10_edges = model.search(protein=protein, residue_number=residue_number, dataset=dataset)
        top_10_edges_dict[dataset] = top_10_edges
    return render_template('search_results.html', top_10_edges_dict=top_10_edges_dict, protein=protein, residue_number=residue_number)

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
    datasets = model.get_datasets()
    for dataset in datasets:
        top_25_edges = model.get_topN_edges(dataset=dataset, n=25)
        top_25_edges_dict[dataset] = top_25_edges
    return render_template('topNedges.html', top_25_edges_dict=top_25_edges_dict)

@app.route('/topN_nodes', methods=['GET','POST'])
def topN_nodes():
    top_25_nodes_dict = {}
    datasets = model.get_datasets()
    for dataset in datasets:
        top_25_nodes = model.get_topN_nodes_with_topM_edges(25, 10, dataset=dataset, cutoff=0.1)
        top_25_nodes_dict[dataset] = top_25_nodes
    return render_template('topNnodes.html', top_25_nodes_dict=top_25_nodes_dict)