/*-------------------------------------------------------------------------
 * Filename:      gtk-thread.c
 * Version:       1.99.1
 * Copyright:     Copyright (C) 1999, Erik Mouw
 * Author:        Erik Mouw <J.A.K.Mouw@its.tudelft.nl>
 * Description:   GTK threads example.
 * Created at:    Sun Oct 17 21:27:09 1999
 * Modified by:   Owen Taylor <otaylor@gtk.org>
 * Modified at:   Wed May 28 10:43:00 2003
 *-----------------------------------------------------------------------*/
/*
 * Compile with:
 *
 * cc -o gtk-thread gtk-thread.c `pkg-config --cflags --libs gtk+-2.0 gthread-2.0`
 *
 * Thanks to Sebastian Wilhelmi for pointing out some bugs in earlier versions.
 *
 */

#include <unistd.h>
#include <gtk/gtk.h>

#define YES_IT_IS    (1)
#define NO_IT_IS_NOT (0)

typedef struct
{
    GtkWidget *text_view;
    int what;
} yes_or_no_args;

G_LOCK_DEFINE_STATIC (yes_or_no);
static volatile int yes_or_no = YES_IT_IS;

void destroy(GtkWidget *widget, gpointer data)
{
    gtk_main_quit();
}

void *argument_thread(void *args)
{
    yes_or_no_args *data = (yes_or_no_args *)args;
    gboolean say_something;

    for(;;)
    {
	/* sleep a while */
	sleep(g_random_int_range (1, 4));

	/* lock the yes_or_no_variable */
	G_LOCK(yes_or_no);

	/* do we have to say something? */
	say_something = (yes_or_no != data->what);

	if(say_something)
	{
	    /* set the variable */
	    yes_or_no = data->what;
	}

	/* Unlock the yes_or_no variable */
	G_UNLOCK(yes_or_no);

	if(say_something)
	{
	    /* get GTK thread lock */
	    gdk_threads_enter();

	    /* set label text */
	    if(data->what == YES_IT_IS) {
		gchar *msg = "Oh yes, it is!\n";
		GtkTextBuffer *buf = gtk_text_view_get_buffer((GtkTextView*)data->text_view);
		GtkTextIter iter;
		gtk_text_buffer_get_end_iter(buf, &iter);
		gint msg_len = (gint) g_utf8_strlen(msg, -1);
		gtk_text_buffer_insert(buf, &iter, msg, msg_len);
	    } else {
		gchar *msg = "Oh no, it isn't!\n";
		GtkTextBuffer *buf = gtk_text_view_get_buffer((GtkTextView*)data->text_view);
		GtkTextIter iter;
		gtk_text_buffer_get_end_iter(buf, &iter);
		gint msg_len = (gint) g_utf8_strlen(msg, -1);
		gtk_text_buffer_insert(buf, &iter, msg, msg_len);
	    }

	    /* Make sure all X commands are sent to the X server; not strictly
	     * necessary here, but always a good idea when you do anything
	     * from a thread other than the one where the main loop is running.
	     */
	    gdk_flush ();

	    /* release GTK thread lock */
	    gdk_threads_leave();
	}
    }

    return NULL;
}

int main(int argc, char *argv[])
{
    GtkWidget *window;
    GtkWidget *text_view;
    GError *error = NULL;
    yes_or_no_args yes_args, no_args;

    /* init threads */
    g_thread_init(NULL);
    gdk_threads_init();

    /* init gtk */
    gtk_init(&argc, &argv);

    /* create a window */
    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_default_size((GtkWindow*) window, 300, 200);

    g_signal_connect(window, "destroy",
	    G_CALLBACK(destroy), NULL);

    gtk_container_set_border_width(GTK_CONTAINER (window), 10);

    /* create a label */
    text_view = gtk_text_view_new();
    gtk_container_add(GTK_CONTAINER(window), text_view);

    /* show everything */
    gtk_widget_show(text_view);
    gtk_widget_show(window);

    /* create the threads */
    yes_args.text_view = text_view;
    yes_args.what = YES_IT_IS;
    if (!g_thread_create(argument_thread, &yes_args, FALSE, &error))
    {
	g_printerr ("Failed to create YES thread: %s\n", error->message);
	return 1;
    }

    no_args.text_view = text_view;
    no_args.what = NO_IT_IS_NOT;
    if (!g_thread_create(argument_thread, &no_args, FALSE, &error))
    {
	g_printerr ("Failed to create NO thread: %s\n", error->message);
	return 1;
    }

    /* enter the GTK main loop */
    gdk_threads_enter();
    gtk_main();
    gdk_threads_leave();

    return 0;
}
