"""
Common Shopify GraphQL queries and mutations.

This module contains reusable GraphQL query and mutation strings for common Shopify operations.
"""


GET_ORDER_DETAILS = """
query GetOrderDetails($name: String!) {
  orders(first: 1, query: $name) {
    edges {
      node {
        id
        name
        number

        # Payment Status
        displayFinancialStatus
        currentTotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }

        # Fulfillment / Shipping Status
        displayFulfillmentStatus

        fulfillments(first: 10) {
          status
          createdAt
          trackingInfo {
            number
            url
          }
          estimatedDeliveryAt
        }

        lineItems(first: 10) {
          edges {
              node {
                  title
                  quantity
              }
          }
        }

        customer {
            firstName
            lastName
            defaultEmailAddress {
              emailAddress
            }
            defaultPhoneNumber {
              phoneNumber
            }
        }

        shippingAddress {
            name
            address1
            city
            province
            zip
            country
        }

        # Order Timeline / Dates
        createdAt
        processedAt   

        # Cancellation Details
        cancelledAt
        cancelReason

      }
    }
  }
}

"""
