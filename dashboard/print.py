import pdfkit

html_code = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        /* Your CSS styles here */
    </style>
</head>

<body>
    <img src="https://i.postimg.cc/hvSB6N1c/amana-logo.png" alt="">
    <h3>HAYY SOUQ, SHARURAH, SAUDI ARABIA</h3>
    <h4>PHONE NO: 00966507328132, EMAIL ID: <a href="">amanathobe@gmail.com</a></h4>
    <h4>WEB SITE: <a href="">www.amanathobe.com </a> VAT NUMNBER/TIM : 310601281900003</h4>

    <h5>CUSTOMER BILL</h5>
    <div class="div1">
        <h4 class="hh">CUSTOMER NAME :</h4>
        <h4 class="hh">CUSTOMER NUMBER :</h4>
        <div class="v1"></div>
        <h4 class="hq">BILL NUMBER :</h4>
        <h4 class="hq1">ORDER DATE :</h4>
        <h4 class="hq2">DELIVERY DATE :</h4>
    </div> <br>
    <table>
        <tr>
            <th>SI NO</th>
            <th>ITEMS</th>
            <th>QTY</th>
            <th>UNIT PRICE</th>
            <th>NET TOTAL</th>
        </tr>
        <tr>
            <td>1</td>
            <td>Thoba</td>
            <td>4</td>
            <td>1000</td>
            <td>4000</td>
        </tr>
        <tr>
            <td>2</td>
            <td>Thoba</td>
            <td>4</td>
            <td>8000</td>
            <td>2900</td>
        </tr>
        <tr>
            <td>3</td>
            <td>Thoba</td>
            <td>6</td>
            <td>1000</td>
            <td>6000</td>
        </tr>
    </table>
    <br>
    <table class="tb1">
        <tr>
            <td>TOTAL :</td>
            <td></td>
        </tr>
        <tr>
            <td>DISCOUNT :</td>
            <td></td>
        </tr>
        <tr>
            <td>GROSS TOTAL :</td>
            <td></td>
        </tr>
        <tr>
            <td>VAT TOTAL : <span>( 15% of Gross Total )</span> </td>
            <td></td>
        </tr>
        <tr>
            <td><b>NET TOTAL : </b><span> ( Gross Total + VAT )</span></td>
            <td></td>
        </tr>
    </table>
</body>

</html>
"""

# Specify the path to the wkhtmltopdf executable
config = pdfkit.configuration(wkhtmltopdf='/path/to/wkhtmltopdf')  # Update this path

# Convert HTML to PDF
pdfkit.from_file(html_code, 'output.pdf', configuration=config)
