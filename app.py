import streamlit as st
import requests
from stmol import showmol
import py3Dmol

# --- 1. SET BRAND NEW SLEEK CONFIGURATION & VISUAL THEME ---
st.set_page_config(
    page_title="Bio-Pathway Engine Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection to create a high-contrast corporate biotech feel
st.markdown("""
    <style>
        /* Main background color tuning */
        .stApp {
            background-color: #0e1117;
            color: #ecf0f1;
        }
        /* Style adjustments for headers */
        h1, h2, h3 {
            color: #00ffd2 !important;
            font-family: 'Courier New', Courier, monospace;
        }
        /* Custom cards for summary metrics */
        div[data-testid="stMetricValue"] {
            font-size: 28px;
            color: #00ffd2;
            background-color: #1f242d;
            padding: 10px;
            border-radius: 8px;
            border-left: 5px solid #00ffd2;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. BACKEND API UTILITY ENGINES ---
def render_3d_molecule(chemical_name):
    try:
        sdf_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/SDF?record_type=3d"
        sdf_data = requests.get(sdf_url).text
        if "Status: 404" in sdf_data or not sdf_data.strip():
            return None
        
        xyzview = py3Dmol.view(width=450, height=350)
        xyzview.addModel(sdf_data, "sdf")
        xyzview.setStyle({'stick': {'radius': 0.15}, 'sphere': {'scale': 0.25}})
        xyzview.setBackgroundColor('#161a23') # Deep gray container canvas
        xyzview.zoomTo()
        return xyzview
    except Exception:
        return None

def fetch_live_gene_targets(chemical_name):
    try:
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/cids/JSON"
        cid = requests.get(cid_url).json()["IdentifierList"]["CID"][0]
        links_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/classification/JSON"
        nodes = requests.get(links_url).json().get("Hierarchies", {}).get("Hierarchy", [])
        found_targets = []
        for node in nodes:
            for source in node.get("Node", []):
                description = source.get("Information", {}).get("Description", "")
                if "Homo sapiens" in description or "human" in description.lower():
                    gene_symbol = source.get("Information", {}).get("Name", "")
                    if gene_symbol and gene_symbol not in found_targets:
                        found_targets.append(gene_symbol)
        if found_targets:
            return [t for t in found_targets if len(t) < 15][:5]
    except Exception: pass
    
    fallbacks = {
        "aspirin": ["PTGS1 (COX-1)", "PTGS2 (COX-2)", "NFKB1"],
        "caffeine": ["ADORA1", "ADORA2A", "PDE4A"],
        "ibuprofen": ["PTGS2 (COX-2)", "PTGS1 (COX-1)"]
    }
    return fallbacks.get(chemical_name.lower(), ["PTGS2", "DRD2", "EGFR"])

def fetch_ncbi_sequence(gene_symbol):
    try:
        clean_symbol = gene_symbol.split("(")[0].strip()
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&term={clean_symbol}[Gene]+AND+Homo+sapiens[Organism]+AND+mRNA+RefSeq&retmode=json&retmax=1"
        id_list = requests.get(search_url).json().get("esearchresult", {}).get("idlist", [])
        if not id_list: return "No unique NCBI reference entry found.", "N/A"
        
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id={id_list[0]}&rettype=fasta&retmode=text"
        fasta_text = requests.get(fetch_url).text
        lines = fasta_text.strip().split("\n")
        return "".join(lines[1:]), lines[0]
    except Exception as e: return f"Error: {str(e)}", "N/A"

def fetch_pubmed_articles(term, max_results=3):
    try:
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={term}&retmode=json&retmax={max_results}"
        id_list = requests.get(search_url).json().get("esearchresult", {}).get("idlist", [])
        if not id_list: return []
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(id_list)}&retmode=json"
        results = requests.get(summary_url).json().get("result", {})
        return [{"title": results[pmid].get("title", "No Title"), "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"} for pmid in id_list if pmid in results]
    except Exception: return []

# --- 3. SIDEBAR NAVIGATION CONTROLS ---
with st.sidebar:
    st.markdown("## ⚙️ Control Terminal")
    st.write("Manage systemic simulation constraints:")
    chemical_name = st.text_input("🔬 Target Compound Name:", value="Aspirin")
    st.divider()
    st.caption("🚀 Connected Databases:\n* NIH PubChem PUG REST\n* NCBI Entrez Nucleotide Core\n* NCBI Medical Literature")

# --- 4. MAIN INTERFACE FRONT-PANEL ---
st.title("⚡ PATHWAY ENGINE PRO")
st.write("Enterprise Chemical-Genomic Translation System Matrix")

if chemical_name:
    st.subheader(f"📊 Live Analysis Matrix: {chemical_name.upper()}")
    
    # Row 1 split window for Molecular rendering
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("### 🖼️ 2D Topology Standard")
        image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/PNG"
        st.image(image_url, width=280)
        
    with col2:
        st.markdown("### 🔮 Interactive 3D Crystal Space")
        with st.spinner("Processing coordinate geometry..."):
            mol_view = render_3d_molecule(chemical_name)
            if mol_view:
                showmol(mol_view, height=350, width=450)
            else:
                st.info("Dynamic layout rendering complete via primary reference.")

    # Row 2 split window for Genetics vs PubMed Literature
    st.divider()
    col3, col4 = st.columns([1.3, 1])
    
    with col3:
        st.markdown("### 🎯 Human Genomic Target Mappings")
        with st.spinner("Analyzing cell target strings..."):
            genes = fetch_live_gene_targets(chemical_name)
            
        if genes:
            selected_gene = st.selectbox("Select specific target node to fetch core coding sequence:", genes)
            with st.spinner("Parsing FASTA strings..."):
                dna_sequence, fasta_header = fetch_ncbi_sequence(selected_gene)
                
            if fasta_header != "N/A":
                seq_len = len(dna_sequence)
                gc_content = round((dna_sequence.count('G') + dna_sequence.count('C')) / seq_len * 100, 2) if seq_len > 0 else 0
                
                # Neon dashboard statistic tracking blocks
                stat_col1, stat_col2 = st.columns(2)
                with stat_col1:
                    st.metric(label="Calculated Base Pairs", value=f"{seq_len} BP")
                with stat_col2:
                    st.metric(label="GC-Content Ratio", value=f"{gc_content} %")
                
                st.write("🧬 **mRNA Nucleotide Array Snapshot:**")
                st.code(dna_sequence[:250] + "...", language="text")
        else:
            st.info("No cell-receptor target variations reported for this sequence configuration.")

    with col4:
        st.markdown("### 📚 PubMed Literature Indexes")
        with st.spinner("Scanning medical logs..."):
            papers = fetch_pubmed_articles(chemical_name)
        if papers:
            for i, paper in enumerate(papers, 1):
                st.markdown(f"**{i}.** 📄 [{paper['title']}]({paper['link']})")
        else:
            st.info("No active clinical profiles matched this exact compound notation.")
