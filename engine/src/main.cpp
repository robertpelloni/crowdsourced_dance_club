#include <libwebsockets.h>
#include <string.h>
#include <stdio.h>
#include <signal.h>
#include <nlohmann/json.hpp>
#include "audio_engine.h"

using json = nlohmann::json;

static int interrupted = 0;
static struct lws *client_wsi = NULL;
AudioEngine engine;

static int callback_dj_conductor(struct lws *wsi, enum lws_callback_reasons reason,
                                void *user, void *in, size_t len)
{
    switch (reason) {
        case LWS_CALLBACK_CLIENT_CONNECTION_ERROR:
            lwsl_err("CLIENT_CONNECTION_ERROR: %s\n",
                     in ? (char *)in : "(null)");
            client_wsi = NULL;
            interrupted = 1;
            break;

        case LWS_CALLBACK_CLIENT_ESTABLISHED:
            lwsl_user("Connection established\n");
            break;

        case LWS_CALLBACK_CLIENT_RECEIVE:
            try {
                std::string msg((char *)in, len);
                json data = json::parse(msg);
                lwsl_user("Received: %s\n", msg.c_str());

                if (data["type"] == "TRACK_SYNC") {
                    engine.handle_track_sync(data["data"]);
                }
            } catch (std::exception &e) {
                lwsl_err("JSON Parse Error: %s\n", e.what());
            }
            break;

        case LWS_CALLBACK_CLIENT_CLOSED:
            client_wsi = NULL;
            interrupted = 1;
            break;

        default:
            break;
    }

    return 0;
}

static const struct lws_protocols protocols[] = {
    { "dj-conductor", callback_dj_conductor, 0, 0 },
    { NULL, NULL, 0, 0 }
};

void sigint_handler(int sig)
{
    interrupted = 1;
}

int main(int argc, char **argv)
{
    struct lws_context_creation_info info;
    struct lws_client_connect_info ccinfo;
    struct lws_context *context;
    const char *p;
    int n = 0;

    signal(SIGINT, sigint_handler);

    memset(&info, 0, sizeof info);
    info.port = CONTEXT_PORT_NO_LISTEN;
    info.protocols = protocols;
    info.gid = -1;
    info.uid = -1;

    context = lws_create_context(&info);
    if (!context) {
        lwsl_err("lws init failed\n");
        return 1;
    }

    memset(&ccinfo, 0, sizeof ccinfo);
    ccinfo.context = context;
    ccinfo.address = "localhost";
    ccinfo.port = 8000;
    ccinfo.path = "/ws/clubgoer";
    ccinfo.host = lws_canonical_hostname(context);
    ccinfo.origin = "origin";
    ccinfo.protocol = protocols[0].name;
    ccinfo.pwsi = &client_wsi;

    lws_client_connect_via_info(&ccinfo);

    if (!engine.initialize()) {
        lwsl_err("Audio Engine init failed\n");
        return 1;
    }
    engine.start();

    while (n >= 0 && !interrupted) {
        n = lws_service(context, 0);
    }

    engine.stop();
    lws_context_destroy(context);

    return 0;
}
