SERVICES={
 "payment-api":{"service":"payment-api","owner":"Payments Platform Team","on_call":"payments-primary","tier":"critical"},
 "card-auth":{"service":"card-auth","owner":"Card Processing Team","on_call":"cards-primary","tier":"critical"},
 "customer-profile":{"service":"customer-profile","owner":"Digital Channels Team","on_call":"channels-primary","tier":"high"},
}
EMPLOYEES={"EMP-1001":{"name":"Asha Perera","department":"Payments","title":"Engineering Manager"}}
async def get_service(name:str)->dict: return SERVICES.get(name,{"error":"service_not_found"})
async def get_employee(employee_id:str)->dict: return EMPLOYEES.get(employee_id,{"error":"employee_not_found"})
