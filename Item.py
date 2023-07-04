class Item:
    def __init__(self, iDProduct, amountProduct, productName, unitValue):
        self.iDProduct = iDProduct
        self.amountProduct = amountProduct
        self.productName = productName
        self.unitValue = unitValue
    
    def get_iDProduct(self):
        return self.iDProduct

    def set_iDProduct(self, iDProduct):
        self.iDProduct = iDProduct

    def get_amountProduct(self):
        return self.amountProduct

    def set_amountProduct(self, amountProduct):
        self.amountProduct = amountProduct

    def get_productName(self):
        return self.productName

    def set_productName(self, productName):
        self.productName = productName

    def get_unitValue(self):
        return self.unitValue

    def set_unitValue(self, unitValue):
        self.unitValue = unitValue
    
