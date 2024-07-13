from ariadne import (
    ObjectType,
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers,
)

from .resolvers import (
    heartbeat_resolver,
    get_quote_resolver,
    get_same_quote_resolver,
    like_quote_resolver,
)


def get_schema():
    query = ObjectType("QueryHandler")
    query.set_field("heartbeat", heartbeat_resolver)
    query.set_field("get_quote_handler", get_quote_resolver)
    query.set_field("get_same_quote_handler", get_same_quote_resolver)

    mutation = ObjectType("MutationHandler")
    mutation.set_field("like_quote_handler", like_quote_resolver)

    type_defs = load_schema_from_path("graphql/quotes.graphql")
    return make_executable_schema(
        type_defs, query, mutation, snake_case_fallback_resolvers
    )
