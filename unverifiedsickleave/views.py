from django.shortcuts import render

# Create your views here.
# TODO: Implement the logic for handling the unverified sick leave balance which automatically upgrades on the basis of accrual rates, and also manage if the balance of the unverified sick leave fills out the upgrade the verified sick leave, always check for the univerified sick leave first of the bank of the unverified sick leave is not full, don't update the verified sick leave balance .
# TODO: Implement the logic for handling the unverified sick leave request and approval process, if approved the deduct the balance of unverified sick leave, while the super user approve the unverified sick leave request, the it should trigger the function in here which deducts the balance it should have all of the logic for handling the balance deduction after approval. Make it as the independent function which does this request.
