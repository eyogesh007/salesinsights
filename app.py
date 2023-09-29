from flask import Flask, render_template, request


app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/ana', methods=['POST'])
def ana():
    return render_template('result.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    import pandas as pd
    import mpld3
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    uploaded_file = request.files['csv_file']
    if uploaded_file.filename != '':
        all_data = pd.read_csv(uploaded_file)
    all_data.head()
    all_data = all_data.dropna(how='all')
    all_data.head()
    all_data = all_data[all_data['Order Date'].str[0:2]!='Or']
    all_data['Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered'])
    all_data['Price Each'] = pd.to_numeric(all_data['Price Each'])
    all_data['Month']=all_data['Order Date'].str[0:2]
    all_data['Month'] = all_data['Month'].astype('int32')
    all_data.head()
    all_data['Month 2'] = pd.to_datetime(all_data['Order Date'], format='%m/%d/%y %H:%M').dt.month
    all_data.head()
    def get_city(address):
        return address.split(",")[1].strip(" ")
    def get_state(address):
        return address.split(",")[2].split(" ")[1]
    all_data['City'] = all_data['Purchase Address'].apply(lambda x: f"{get_city(x)}  ({get_state(x)})")
    all_data.head()
    all_data['Sales'] = all_data['Quantity Ordered'].astype('int') * all_data['Price Each'].astype('float')
    all_data.groupby(['Month']).sum()
    months = range(1,13)
    plt.title('Total Sales as per month')
    plt.bar(months,all_data.groupby(['Month']).sum()['Sales'])
    plt.xticks(months)
    plt.ylabel('Sales in USD ($)')
    plt.xlabel('Month number')
    html_fig1 = mpld3.fig_to_html(plt.gcf())
    city_sales = all_data.groupby('City').sum()['Sales']
    fig, ax = plt.subplots(figsize=(10, 6))
    city_sales.plot(kind='bar')
    plt.title('Total Sales by City')
    plt.xlabel('City')
    plt.ylabel('Total Sales (USD)')
    product_list=city_sales.index
    plt.xticks(range(len(city_sales.index)), labels=city_sales.index, rotation=45)
    html_fig2 = mpld3.fig_to_html(fig)
    all_data['Order Date'] = pd.to_datetime(all_data['Order Date'], format='%m/%d/%y %H:%M')
    all_data['Hour'] = all_data['Order Date'].dt.hour
    all_data['Minute'] = all_data['Order Date'].dt.minute
    all_data['Count'] = 1
    all_data.head()
    plt.figure(figsize=(10,6))
    all_data.groupby(['Hour']).count()['Count'].plot(kind='bar', color='skyblue')
    plt.xlabel('Hour')
    plt.ylabel('Number of Orders')
    plt.title('Number of Orders at Each Hour')
    plt.xticks(rotation=0)
    plt.grid(axis='y', alpha=0.75)
    html_fig3 = mpld3.fig_to_html(plt.gcf())

    product_group = all_data.groupby('Product')
    all_data['Order Date'] = pd.to_datetime(all_data['Order Date'], format='%m/%d/%y %H:%M')
    all_data['Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered'], errors='coerce')
    all_data = all_data.dropna(subset=['Quantity Ordered'])
    quantity_ordered = all_data.groupby('Product')['Quantity Ordered'].sum()
    keys = [str(pair) for pair, df in product_group]
    plt.figure(figsize=(10,6))
    plt.bar(keys, quantity_ordered)
    plt.xticks(keys, rotation='vertical', size=8)
    html_fig4 = mpld3.fig_to_html(plt.gcf())
    qo=keys
    all_data['Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered'])
    all_data['Price Each'] = pd.to_numeric(all_data['Price Each'])
    all_data['Profit'] = all_data['Quantity Ordered'] * all_data['Price Each']
    product_profit = all_data.groupby('Product')['Profit'].sum()
    top_10_products = product_profit.nlargest(10)
    top_products = top_10_products.index.tolist()
    plt.figure(figsize=(10, 6))
    top_10_products.plot(kind='bar', color='skyblue')
    plt.xlabel('Product')
    plt.ylabel('Total Profit (USD)')
    plt.title('Top 10 Products by Profit')
    plt.xticks(rotation=45)
    html_fig6 = mpld3.fig_to_html(plt.gcf())
    all_data['Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered'])
    category_sales = all_data.groupby('Category')['Quantity Ordered'].sum()
    plt.figure(figsize=(10, 6))
    plt.pie(category_sales, labels=category_sales.index, autopct='%1.1f%%', startangle=140, colors=['skyblue', 'lightcoral', 'lightgreen'])
    plt.title('Most Selling Category')
    plot7 = mpld3.fig_to_html(plt.gcf())

    prices = all_data.groupby('Product')['Price Each'].mean()
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.bar(keys, quantity_ordered, color='g', label='Quantity Ordered')
    ax1.set_xlabel('Product Name')
    ax1.set_ylabel('Quantity Ordered', color='g')
    ax2.plot(keys, prices, color='b', label='Price ($)')
    ax2.set_ylabel('Price ($)', color='b')
    ax1.set_xticks(range(len(keys)))
    ax1.set_xticklabels(keys, rotation='vertical', fontsize=8)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    html_fig5 = mpld3.fig_to_html(plt.gcf())
    return render_template('result.html', plot=html_fig1,plot2=html_fig2, plot3=html_fig3,plot4=html_fig4,plot5=html_fig5,plot6=html_fig6,plot7=plot7,product_list=product_list,qo=qo,month=["January","February","March","April","May","June","July","August","September","October","November","December"],top_products=top_products)

if __name__ == '__main__':
    app.run()
