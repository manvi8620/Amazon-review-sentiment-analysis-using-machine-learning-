import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from text_summary import run_summarization

# Function to truncate text for display
def truncate_text(text, max_length=200):
    return text if len(text) <= max_length else text[:max_length] + "..."

def enter_data(selected_var, file_1):
    target_keyword = selected_var.get()
    if target_keyword:
        df = pd.read_csv(file_1)
        df = df.drop_duplicates(subset=['review'])

        text_list = df[df['name'] == target_keyword]['review'].values
        text_list = [review.lower() for review in text_list if isinstance(review, str)]

        # Handle NaN reviews before joining
        reviews_grouped = df.groupby('name')['review'].apply(lambda x: ' '.join(x.fillna(''))).reset_index()
        reviews_grouped.rename(columns={'review': 'combine_reviews'}, inplace=True)

        # Get the concatenated reviews for summarization
        backend = reviews_grouped[reviews_grouped['name'] == target_keyword]['combine_reviews'].values[0]
        backend = backend.lower()

        # final_result,conclusion = run_summarization(backend)
        final_result, conclusion, pos_sentences, neg_sentences, neu_sentences = run_summarization(backend)

        # print(f"{final_result}-----------------")

        if final_result:
            return text_list, final_result,conclusion,pos_sentences, neg_sentences, neu_sentences
    else:
        messagebox.showwarning("Validation Error", "Please select a Product.")
    return None, None




def fetch_all_campaign_options(file_1):
    df = pd.read_csv(file_1)
    return df['name'].drop_duplicates().to_list()


def plot_graph(conclusion, graph_frame):
    plt.close('all')

    data = {'Category': ['mixed', 'negative', 'positive'], 'Accuracy': [0.55, 0.82, 0.89]}
    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(8, 6))  # Specify canvas size
    bars = ax.bar(df['Category'], df['Accuracy'], color=['gray', 'red', 'green'], width=0.3)

    colors = {'positive': 'green', 'negative': 'red', 'mixed': 'blue'}
    predicted_index = df[df['Category'] == conclusion].index[0]

    ax.scatter(predicted_index, df.loc[predicted_index, 'Accuracy'], 
                color=colors[conclusion], s=300, marker='o', edgecolors='black', label=f'Predicted: {conclusion}')
    ax.set_xlabel('Sentiment Category')
    ax.set_ylabel('Accuracy')
    ax.set_title('Sentiment Prediction vs Accuracy')
    ax.legend()

    for widget in graph_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor='center', width=600, height=450)  # Centering the graph
def plot_summary_breakdown(pos_sentences, neg_sentences, neu_sentences, parent_frame):
    counts = [len(pos_sentences), len(neg_sentences), len(neu_sentences)]
    labels = ['Positive', 'Negative', 'Neutral']
    # Pastel color palette
    colors = ['#A8E6CF', '#FF8B94', '#DCE1F2']

    fig, ax = plt.subplots(figsize=(4, 4))
    
    # Create pie chart with shadow and start angle adjustment
    wedges, texts, autotexts = ax.pie(
        counts, 
        labels=labels, 
        colors=colors, 
        autopct='%1.1f%%', 
        startangle=140, 
        shadow=True,
        textprops={'fontsize': 10, 'color': 'black'}
    )
    
    # Add legend at the bottom center
    ax.legend(wedges, labels, title="Sentiments", loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=3)
    
    # Set title with styling
    ax.set_title("Summary Sentiment Breakdown", fontsize=14, fontweight='bold', pad=10)
    
    # Optionally, add a white circle in the center for a donut effect
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(centre_circle)
    
    # Clear the parent frame and embed the canvas
    for widget in parent_frame.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def main_exe(file_1):
    root = tk.Tk()
    root.title("Amazon Product Review Summarization")
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))

    # Cross-platform full screen
    try:
        root.state('zoomed')  # Windows
    except:
        root.attributes('-zoomed', True)  # Linux
    roboto_slab = tkFont.Font(family="Roboto Slab", size=20, weight="bold")

    # ---------------- Layout Frames ----------------
    left_frame = tk.Frame(root, bg="#FCEEF5", width=800)
    left_frame.pack(side="left", fill="both", expand=False)

    middle_frame = tk.Frame(root, bg="#E0F7FA", width=500)
    middle_frame.pack(side="left", fill="both", expand=True)

# ---------------- Right Frame with Scrollbar ----------------
    right_frame_container = tk.Frame(root, bg="#FCEEF5", width=350)
    right_frame_container.pack(side="right", fill="both", expand=False)

    # Canvas for scrollable content
    canvas = tk.Canvas(right_frame_container, bg="#FCEEF5", width=350)
    canvas.pack(side="left", fill="both", expand=True)

    # Vertical scrollbar
    scrollbar = tk.Scrollbar(right_frame_container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Content Frame to hold widgets
    right_frame = tk.Frame(canvas, bg="#FCEEF5", width=350)
    canvas.create_window((0, 0), window=right_frame, anchor="nw")

    # Adjust scrolling region
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    right_frame.bind("<Configure>", on_frame_configure)


    # ---------------- Left Frame - Inputs ----------------
    tk.Label(left_frame, text="Text Summarization", font=(roboto_slab, 24), bg="#FCEEF5").pack(pady=20)

    selected_var = tk.StringVar()
    campaign_frame = tk.LabelFrame(left_frame, text="Product Info", font=(roboto_slab, 16), bg="#FCEEF5")
    campaign_frame.pack(padx=20, pady=20, fill='x')

    tk.Label(campaign_frame, text="Select Product", font=(roboto_slab, 14), bg="#FCEEF5").grid(row=0, column=0)
    product_combobox = ttk.Combobox(campaign_frame, textvariable=selected_var, values=fetch_all_campaign_options(file_1), font=(roboto_slab, 12))
    product_combobox.grid(row=0, column=1, padx=20,pady=20)
    product_combobox.set("Select your Product")

    # Summary Section
    summary_label = tk.Label(left_frame, text="Summary", font=(roboto_slab, 16), bg="#FCEEF5")
    summary_label.pack(pady=10)

    summary_text = tk.Text(left_frame, height=10, width=40, font=(roboto_slab, 12))
    summary_text.pack(pady=10)

    conclusion_label = tk.Label(left_frame, text="", font=(roboto_slab, 14), fg="green", bg="#FCEEF5")
    conclusion_label.pack()

    # ---------------- Submit Function ----------------
    def submit_and_close():
        if not selected_var.get() or selected_var.get() == "Select your Product":
            messagebox.showwarning("Validation Error", "Please select a Product.")
            return

        user_reviews, final_summary, conclusion,pos_sentences, neg_sentences, neu_sentences, = enter_data(selected_var, file_1)

        if user_reviews is not None and len(user_reviews) > 0 and final_summary:
            # Clear previous review tiles from right_frame
            for widget in right_frame.winfo_children():
                widget.destroy()

            # Create review tiles with one review per row and set height
            for idx, review in enumerate(user_reviews):
                tile = tk.Frame(right_frame, bg="#FCEEF5", bd=2, relief="sunken", padx=5, pady=5, height=150,width=200)
                tile.grid(row=idx, column=0, padx=10, pady=10, sticky="nsew")
                tile.grid_propagate(False)  # Prevent the frame from resizing to fit its content

                # Allow the tile to expand horizontally
                right_frame.grid_columnconfigure(0, weight=1)

                # review_label = tk.Label(tile, text=f"Review {idx + 1}", font=(roboto_slab, 14, "bold"), bg="#FFCEDF")
                # review_label.pack(anchor="w")

                # Adjust width (here 300 pixels) as needed
                review = truncate_text(review, max_length=200)
                review_text = tk.Message(tile, text=review, width=300, font=(roboto_slab, 12), bg="#f9f9f9")
                review_text.pack(padx=5, pady=5)

            # Display the generated summary on the left side
            summary_text.delete(1.0, tk.END)
            summary_text.insert(tk.END, final_summary)
            ft="Overall Review is : "+conclusion
            conclusion_label.config(text=ft)
            # plot_graph(conclusion, middle_frame)
            plot_summary_breakdown(pos_sentences, neg_sentences, neu_sentences, parent_frame=middle_frame)


    submit_button = tk.Button(left_frame, text="Submit", font=(roboto_slab, 16), command=submit_and_close, bg="green", fg="white")
    submit_button.pack(pady=20)

    root.mainloop()


