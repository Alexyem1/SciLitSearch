import streamlit as st
from pymed import PubMed
from st_aggrid import AgGrid
import pandas as pd  # Import pandas for DataFrame support
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
from streamlit_extras.app_logo import add_logo


# Streamlit app layout
# Set the page to wide mode
st.set_page_config(layout="wide")

def logo():
    add_logo("logo2.png", height=300)

def fetch_publications_deprecated(query, max_results=500):
    pubmed = PubMed(tool="MyTool", email="my@email.address")
    results = pubmed.query(query, max_results=max_results)

    publications = []
    for article in results:
        #st.write(article)
        pubmed_id = article.pubmed_id.split('\n')[0]  # Clean the PMID
        article_link = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}"

        if article.keywords:
            if None in article.keywords:
                article.keywords.remove(None)
            keywords = '", "'.join(article.keywords)
        
        publications.append({
            "PubMed ID": pubmed_id,
            "Title": article.title,
            "Abstract": article.abstract if article.abstract else "N/A",  # Handle missing abstracts
            "Journal": article.journal,
            "Publication Date": article.publication_date,
            #"Authors": ", ".join([author['lastname'] + " " + author.get('initials', '') for author in article.authors]),
            "Authors": ", ".join([str(author.get('lastname', '')) + " " + str(author.get('initials', '')) for author in article.authors]),
            "Keywords": keywords,

            "Link": article_link
        })
    return pd.DataFrame(publications)  # Convert the list of dictionaries to a DataFrame




def fetch_publications_old(query, max_results=500):
    pubmed = PubMed(tool="MyTool", email="my@email.address")
    results = pubmed.query(query, max_results=max_results)

    publications = []
    for article in results:
        pubmed_id = article.pubmed_id.split('\n')[0]  # Clean the PMID
        article_link = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}"

        # Initialize keywords variable for each article
        keywords = 'Not Available'  # Default value if no keywords
        if article.keywords:
            # Remove None values if present
            cleaned_keywords = [kw for kw in article.keywords if kw is not None]
            # Join the keywords into a single string, if keywords exist
            if cleaned_keywords:
                keywords = '", "'.join(cleaned_keywords)

        # Handle authors similarly, ensuring clean initialization
        authors = [str(author.get('lastname', '')) + " " + str(author.get('initials', '')) for author in article.authors] if article.authors else ["Unknown Author"]

        publications.append({
            "PubMed ID": pubmed_id,
            "Title": article.title,
            "Abstract": article.abstract if article.abstract else "N/A",
            "Journal": article.journal if article.journal else "Not Available",
            "Publication Date": article.publication_date if article.publication_date else "Not Available",
            "Authors": ", ".join(authors),
            "Keywords": keywords,
            "Link": article_link
        })
    return pd.DataFrame(publications)  # Convert the list of dictionaries to a DataFrame




def fetch_publications(query, max_results=500):
    pubmed = PubMed(tool="MyTool", email="my@email.address")
    results = pubmed.query(query, max_results=max_results)

    publications = []
    for article in results:
        pubmed_id = article.pubmed_id.split('\n')[0]  # Clean the PMID
        article_link = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}"

        # Initialize keywords variable for each article
        keywords = 'Not Available'  # Default value if no keywords
        if hasattr(article, 'keywords') and article.keywords:
            cleaned_keywords = [kw for kw in article.keywords if kw is not None]
            keywords = '", "'.join(cleaned_keywords) if cleaned_keywords else 'Not Available'

        # Safely access the journal attribute
        journal = article.journal if hasattr(article, 'journal') and article.journal else "Not Available"

        # Handle authors, ensuring each has a default value if missing
        authors = [str(author.get('lastname', '')) + " " + str(author.get('initials', '')) for author in article.authors] if hasattr(article, 'authors') and article.authors else ["Unknown Author"]

        publications.append({
            "PubMed ID": pubmed_id,
            "Title": article.title,
            "Abstract": article.abstract if hasattr(article, 'abstract') and article.abstract else "N/A",
            "Journal": journal,
            "Publication Date": article.publication_date if hasattr(article, 'publication_date') and article.publication_date else "Not Available",
            "Authors": ", ".join(authors),
            "Keywords": keywords,
            "Link": article_link
        })
    return pd.DataFrame(publications)  # Convert the list of dictionaries to a DataFrame










def display_results_in_aggrid(pubmed_results):
    email = 'your@email.com'  # Update with your email

    # Convert to DataFrame (assuming pubmed_results is already a DataFrame or similar structure)
    df = pubmed_results

    # Create AgGrid options
    grid_options = GridOptionsBuilder.from_dataframe(df)
    grid_options.configure_selection('multiple', use_checkbox=True)

    # Display the AgGrid table with checkboxes
    with st.expander("AgGrid Table"):
        grid_result = AgGrid(
            df,
            gridOptions=grid_options.build(),
            enable_enterprise_modules=False,
        )

    # Get selected rows
    selected_rows = grid_result['selected_rows']
    #st.write(selected_rows)

    # Display detailed information for selected rows
    if selected_rows:
#         print(selected_rows)
        st.subheader("Selected Publication Details:")
        for row in selected_rows:
            # Define CSS styles
            styles = """
            <style>
                .publication-info {
                    font-family: Arial, sans-serif;
                    margin-bottom: 20px;
                }
                .publication-title {
                    font-weight: bold;
                    font-size: 20px;
                    color: #d66e13;
                }
                .publication-header {
                    font-weight: bold;
                }
            </style>
            """

            # Structured publication information
            publication_info = f"""
            {styles}
            <div class="publication-info">
                <div class="publication-title">{row["Title"]}</div>
                <div><span class="publication-header">PubMed-ID:</span> {row["PubMed ID"]}</div>
                <div><span class="publication-header">Journal:</span> {row["Journal"]}</div>
                <div><span class="publication-header">Authors:</span> {row["Authors"]}</div>
                <div><span class="publication-header">Published:</span> {row["Publication Date"]}</div>
                <div><span class="publication-header">Keywords:</span> {row["Keywords"]}</div>
                <div><span class="publication-header">URL:</span> <a href="{row["Link"]}" target="_blank">Link to paper</a></div>
            </div>
            """

            # Use markdown to render the styled publication information
            #st.markdown(publication_info, unsafe_allow_html=True)

            # Display abstract with an expander
            #with st.expander("**Abstract:**"):
            #    st.write(row["Abstract"])
            
            # Display abstract with an expander and custom styling
            with st.expander(">>>",expanded=True):
                # Define the CSS for the abstract container and the title
                abstract_style = """
                <style>
                    .abstract-title {{
                        font-weight: bold;
                        font-size: 20px;  /* Adjust the size as needed */
                        margin-bottom: 10px;  /* Space below the title */
                    }}
                    .abstract-container {{
                        background-color: #e0f2fe;  /* Light blue background */
                        border-left: 5px solid #2196f3;  /* Darker blue border for some contrast */
                        padding: 10px;  /* Some padding around the text */
                        margin: 10px 0;  /* Margin at the top and bottom */
                        border-radius: 5px;  /* Rounded corners */
                    }}
                </style>
                <div class="abstract-title">Abstract:</div>
                <div class="abstract-container">
                    {abstract}
                </div>
                """.format(abstract=row["Abstract"])

                st.markdown(publication_info, unsafe_allow_html=True)

                # Use markdown to render the styled abstract container and title, allowing HTML
                st.markdown(abstract_style, unsafe_allow_html=True)



def calculate_journal_distribution(pubmed_results):

    results = pubmed_results

    journal_counts = {}
    for article in results["Journal"]:
        # Access the journal name directly from the article variable
        journal = str(article) if article else "No journal available"
        
        journal_counts[journal] = journal_counts.get(journal, 0) + 1

    return journal_counts     

def calculate_journal_distribution_optimized(pubmed_results):
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(pubmed_results)

    # Ensure there's a "Journal" column; fill missing values with a placeholder
    df["Journal"] = df.get("Journal", "No journal available")

    # Calculate journal counts
    journal_counts = df["Journal"].value_counts().reset_index()
    journal_counts.columns = ["Journal", "Count"]

    return journal_counts  

from pymed import PubMed

def calculate_author_publication_counts(pubmed_results):
    
    results = pubmed_results

    author_counts = {}
    for author in results["Authors"]:
        author_list = author.split(",")
        # Note: Ensure that 'Authors' is the correct attribute based on pymed documentation
        # Increment count for each author
        #author_counts[author] = author_counts.get(author, 0) + 1

        for author in author_list:
            #st.write(author)
            # Trim any leading/trailing whitespace that might be left after splitting
            trimmed_author = author.strip()
            if trimmed_author and trimmed_author != "None None":
            # Increment count for each author
                author_counts[trimmed_author] = author_counts.get(trimmed_author, 0) + 1

    return author_counts




st.title('PubMed Publication Retrieval')
st.sidebar.image("./logo.webp", use_column_width=True)
query = st.text_input("Enter your search query", "")
max_results = st.number_input("Max results", min_value=10, max_value=1000, value=500)


if st.button("Search", key="Pubmed") or 'pubmed_results' in st.session_state:
    with st.spinner('Fetching publications...'):
        if 'pubmed_results' not in st.session_state or st.session_state.query != query:
            # Fetch and store the results in session state
            st.session_state.pubmed_results = fetch_publications(query)
            st.session_state.query = query
        if not st.session_state.pubmed_results.empty:
                        # Plots
            tab1, tab2, tab3, tab4 = st.tabs(["Table","Pie chart", "Author Network", "TOP10 Bar plot"])
            with tab1:
                # Display the results using AgGrid
                display_results_in_aggrid(st.session_state.pubmed_results)
            with tab2:
                # Display Journal Distribution
                # Calculate journal distribution
                #journal_distribution = calculate_journal_distribution(st.session_state.pubmed_results)
                journal_distribution_df = calculate_journal_distribution_optimized(st.session_state.pubmed_results)


                # Create a DataFrame for the pie chart
                #journal_distribution_df = pd.DataFrame(journal_distribution.items(), columns=["Journal", "Count"])

                # Create an interactive pie chart using Plotly Express
                fig1 = px.pie(
                    #journal_distribution_df,
                    journal_distribution_df.nlargest(10, 'Count'),  # Display top 20 for better visualization
                    names="Journal",
                    values="Count",
                    title="Journal Distribution",
                    labels={"Journal": "Journal", "Count": "Count"},
                )

                # Customize the layout of the chart
                fig1.update_layout(
                    legend_title_text="Journal",
                    margin=dict(l=0, r=0, t=30, b=0),  # Adjust chart margin
                )

                # Create an interactive bar chart using Plotly Express for better readability with many categories
                fig = px.bar(
                    journal_distribution_df.nlargest(20, 'Count'),  # Display top 20 for better visualization
                    x='Journal',
                    y='Count',
                    title='Journal Distribution',
                    labels={'Journal': 'Journal', 'Count': 'Count'},
                )

                # Customize the layout of the chart
                fig.update_layout(
                    xaxis={'categoryorder': 'total descending'},
                    yaxis_title="Publication Count",
                    xaxis_title="Journal",
                    #margin=dict(l=0, r=0, t=30, b=0),
                )

                # Render the Plotly figure
                st.plotly_chart(fig1)


        
            with tab4:
                # Calculate author publication counts
                author_counts = calculate_author_publication_counts(st.session_state.pubmed_results)

                # Sort authors by publication counts in descending order and select the top 10
                top_authors = dict(sorted(author_counts.items(), key=lambda item: item[1], reverse=True)[:10])

                # Create a DataFrame for the barplot
                top_authors_df = pd.DataFrame(top_authors.items(), columns=["Author", "Publication Count"])

                # Create an interactive bar chart using Plotly Express
                fig = px.bar(
                    top_authors_df,
                    x="Author",
                    y="Publication Count",
                    color="Author",  # Assign different colors to authors
                    title="Top 10 Authors by Publication Count",
                    labels={"Author": "Authors", "Publication Count": "Publication Count"},
                )

                # Customize the layout of the chart
                fig.update_layout(
                    xaxis=dict(tickangle=45),  # Rotate labels for readability
                    xaxis_title="Authors",  # X-axis name
                    yaxis_title="Publication Count",  # Y-axis name
                    showlegend=False,  # Hide the legend
                )

                # Render the Plotly figure
                st.plotly_chart(fig)

        else:
            st.write("No publications found.")


