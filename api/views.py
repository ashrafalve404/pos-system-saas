from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

from organizations.models import APIKey
from products.models import Product, Category
from stores.models import Store


@csrf_exempt
@require_http_methods(["POST"])
def add_product(request):
    """Add a product via API key authentication"""
    api_key = request.headers.get('X-API-Key')
    
    if not api_key:
        return JsonResponse({'error': 'API key required. Use X-API-Key header.'}, status=401)
    
    organization = APIKey.get_organization_from_key(api_key)
    if not organization:
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    try:
        import json
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    
    name = data.get('name')
    price = data.get('price')
    
    if not name:
        return JsonResponse({'error': 'Product name is required'}, status=400)
    if not price:
        return JsonResponse({'error': 'Product price is required'}, status=400)
    
    try:
        price = Decimal(str(price))
    except:
        return JsonResponse({'error': 'Invalid price format'}, status=400)
    
    category_name = data.get('category', 'Uncategorized')
    category, _ = Category.objects.get_or_create(
        organization=organization,
        name=category_name,
        defaults={'description': f'Products in {category_name} category'}
    )
    
    store_id = data.get('store_id')
    if store_id:
        store = Store.objects.filter(id=store_id, organization=organization).first()
    else:
        store = Store.objects.filter(organization=organization, is_active=True).first()
    
    if not store:
        return JsonResponse({'error': 'No store found. Please create a store first.'}, status=400)
    
    sku = data.get('sku')
    if sku:
        product = Product.objects.filter(organization=organization, sku=sku).first()
    else:
        product = Product.objects.filter(organization=organization, name=name).first()
    
    if product:
        product.price = price
        product.category = category
        product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
        product.description = data.get('description', product.description)
        product.barcode = data.get('barcode', product.barcode)
        product.is_active = data.get('is_active', True)
        product.save()
        return JsonResponse({
            'success': True,
            'message': 'Product updated successfully',
            'product_id': product.id,
            'product_name': product.name
        })
    else:
        product = Product.objects.create(
            organization=organization,
            name=name,
            sku=sku or f'PROD-{Product.objects.filter(organization=organization).count() + 1:04d}',
            category=category,
            store=store,
            price=price,
            stock_quantity=data.get('stock_quantity', 0),
            low_stock_threshold=data.get('low_stock_threshold', 10),
            description=data.get('description', ''),
            barcode=data.get('barcode', ''),
            is_active=True
        )
        return JsonResponse({
            'success': True,
            'message': 'Product created successfully',
            'product_id': product.id,
            'product_name': product.name
        })


@csrf_exempt
@require_http_methods(["POST"])
def add_products_bulk(request):
    """Add multiple products via API key authentication"""
    api_key = request.headers.get('X-API-Key')
    
    if not api_key:
        return JsonResponse({'error': 'API key required. Use X-API-Key header.'}, status=401)
    
    organization = APIKey.get_organization_from_key(api_key)
    if not organization:
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    try:
        import json
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    
    products_data = data.get('products', [])
    if not products_data:
        return JsonResponse({'error': 'No products provided'}, status=400)
    
    store_id = data.get('store_id')
    if store_id:
        store = Store.objects.filter(id=store_id, organization=organization).first()
    else:
        store = Store.objects.filter(organization=organization, is_active=True).first()
    
    if not store:
        return JsonResponse({'error': 'No store found. Please create a store first.'}, status=400)
    
    results = []
    errors = []
    
    for i, prod_data in enumerate(products_data):
        try:
            name = prod_data.get('name')
            price = prod_data.get('price')
            
            if not name or not price:
                errors.append(f'Row {i+1}: Name and price required')
                continue
            
            try:
                price = Decimal(str(price))
            except:
                errors.append(f'Row {i+1}: Invalid price format')
                continue
            
            category_name = prod_data.get('category', 'Uncategorized')
            category, _ = Category.objects.get_or_create(
                organization=organization,
                name=category_name,
                defaults={'description': f'Products in {category_name} category'}
            )
            
            sku = prod_data.get('sku')
            if sku:
                product = Product.objects.filter(organization=organization, sku=sku).first()
            else:
                product = Product.objects.filter(organization=organization, name=name).first()
            
            if product:
                product.price = price
                product.category = category
                product.stock_quantity = prod_data.get('stock_quantity', product.stock_quantity)
                product.description = prod_data.get('description', product.description)
                product.barcode = prod_data.get('barcode', product.barcode)
                product.is_active = prod_data.get('is_active', True)
                product.save()
                results.append({'id': product.id, 'name': product.name, 'action': 'updated'})
            else:
                product = Product.objects.create(
                    organization=organization,
                    name=name,
                    sku=sku or f'PROD-{Product.objects.filter(organization=organization).count() + 1:04d}',
                    category=category,
                    store=store,
                    price=price,
                    stock_quantity=prod_data.get('stock_quantity', 0),
                    low_stock_threshold=prod_data.get('low_stock_threshold', 10),
                    description=prod_data.get('description', ''),
                    barcode=prod_data.get('barcode', ''),
                    is_active=True
                )
                results.append({'id': product.id, 'name': product.name, 'action': 'created'})
                
        except Exception as e:
            errors.append(f'Row {i+1}: {str(e)}')
    
    return JsonResponse({
        'success': True,
        'message': f'Processed {len(results)} products',
        'results': results,
        'errors': errors
    })


@require_http_methods(["GET"])
def api_docs(request):
    """API documentation"""
    return JsonResponse({
        'name': 'SaaS POS API',
        'version': '1.0',
        'description': 'API for syncing products to your POS system',
        'endpoints': {
            'POST /api/products/add/': {
                'description': 'Add or update a single product',
                'headers': {'X-API-Key': 'your-api-key-here'},
                'body_fields': {
                    'name': 'Product name (required)',
                    'price': 'Product price (required)',
                    'category': 'Category name (optional)',
                    'sku': 'SKU (optional)',
                    'barcode': 'Barcode (optional)',
                    'stock_quantity': 'Stock quantity (optional)',
                    'description': 'Product description (optional)',
                    'store_id': 'Store ID (optional)'
                }
            },
            'POST /api/products/bulk/': {
                'description': 'Add or update multiple products',
                'headers': {'X-API-Key': 'your-api-key-here'},
                'body_fields': {
                    'products': '[Array of product objects]',
                    'store_id': 'Store ID (optional)'
                }
            },
            'POST /api/products/import/': {
                'description': 'Import products from external URL',
                'headers': {'X-API-Key': 'your-api-key-here'},
                'body_fields': {
                    'url': 'External API URL (required)',
                    'api_key': 'External API key (optional)',
                    'field_mapping': 'Map external fields to internal fields (optional)',
                    'category': 'Default category for imported products (optional)'
                }
            }
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def import_products(request):
    """Import products from external API URL"""
    api_key = request.headers.get('X-API-Key')
    
    if not api_key:
        return JsonResponse({'error': 'API key required'}, status=401)
    
    organization = APIKey.get_organization_from_key(api_key)
    if not organization:
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    try:
        import json
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    
    external_url = data.get('url')
    if not external_url:
        return JsonResponse({'error': 'External URL is required'}, status=400)
    
    # Fetch from external API
    import urllib.request
    import urllib.error
    import ssl
    
    # Create SSL context that doesn't verify certificates (for development)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    if data.get('api_key'):
        headers['X-API-Key'] = data.get('api_key')
    
    try:
        req = urllib.request.Request(external_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            external_data = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return JsonResponse({'error': 'External API blocked the request. This API may require authentication or be rate-limited.'}, status=400)
        return JsonResponse({'error': f'External API error: {e.code}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Failed to fetch: {str(e)}'}, status=400)
    
    # Normalize to list
    if isinstance(external_data, dict):
        if 'products' in external_data:
            products_list = external_data['products']
        elif 'data' in external_data:
            products_list = external_data['data']
        else:
            products_list = [external_data]
    else:
        products_list = external_data
    
    # Field mapping
    field_map = data.get('field_mapping', {})
    if not field_map:
        # Auto-detect common external API formats
        if products_list and len(products_list) > 0:
            sample = products_list[0]
            if 'title' in sample and 'name' not in sample:
                field_map = {'name': 'title', 'price': 'price', 'description': 'description', 'image': 'image'}
            if 'image' in sample and 'barcode' not in sample:
                field_map['image'] = 'image'
    
    default_category = data.get('category', 'Imported')
    
    # Get store
    store_id = data.get('store_id')
    if store_id:
        store = Store.objects.filter(id=store_id, organization=organization).first()
    else:
        store = Store.objects.filter(organization=organization, is_active=True).first()
    
    if not store:
        return JsonResponse({'error': 'No store found'}, status=400)
    
    # Create category
    category, _ = Category.objects.get_or_create(
        organization=organization,
        name=default_category,
        defaults={'description': 'Imported products'}
    )
    
    results = []
    errors = []
    
    for i, prod in enumerate(products_list):
        try:
            # Map fields
            name = prod.get(field_map.get('name', 'name')) or prod.get('title', 'Product ' + str(i+1))
            price = prod.get(field_map.get('price', 'price'))
            description = prod.get(field_map.get('description', 'description'), '')
            
            if not name:
                errors.append(f'Row {i+1}: No name found')
                continue
            
            if not price:
                # Try to find price in different formats
                if 'price' in prod:
                    price = prod['price']
                    if isinstance(price, dict):
                        price = price.get('amount') or price.get('value')
                else:
                    errors.append(f'Row {i+1}: No price found')
                    continue
            
            try:
                price = float(price)
            except:
                errors.append(f'Row {i+1}: Invalid price')
                continue
            
            # Check if exists by title (for fakestoreapi)
            product = Product.objects.filter(organization=organization, name=name).first()
            
            if product:
                product.price = price
                product.description = description[:500] if description else ''
                product.save()
                results.append({'id': product.id, 'name': name, 'action': 'updated'})
            else:
                product = Product.objects.create(
                    organization=organization,
                    name=name[:200],
                    sku=f'IMP-{Product.objects.filter(organization=organization).count() + 1:05d}',
                    category=category,
                    store=store,
                    price=price,
                    stock_quantity=10,
                    low_stock_threshold=5,
                    description=description[:500] if description else '',
                    is_active=True
                )
                results.append({'id': product.id, 'name': name, 'action': 'created'})
                
        except Exception as e:
            errors.append(f'Row {i+1}: {str(e)}')
    
    return JsonResponse({
        'success': True,
        'message': f'Imported {len(results)} products',
        'results': results,
        'errors': errors[:10]  # Limit errors shown
    })
